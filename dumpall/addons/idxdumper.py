#!/usr/bin/env python3
# -*- coding=utf-8 -*-

"""
    适用于开启index页面的网站，如apache index
"""

import asyncio
import aiohttp
from urllib.parse import urlparse, urljoin
from asyncio.queues import Queue
from pyquery import PyQuery as pq
from ..dumper import BaseDumper


class Dumper(BaseDumper):
    """ index dumper """

    def __init__(self, url: str, outdir: str, **kwargs):
        super(Dumper, self).__init__(url, outdir, **kwargs)
        self.netloc = urlparse(url).netloc
        self.fetched_urls = []
        self.task_count = 10  # 协程数量
        self.running = False

    async def start(self):
        """ 入口方法 """
        # queue必须创建在run()方法内 https://stackoverflow.com/questions/53724665/using-queues-results-in-asyncio-exception-got-future-future-pending-attached
        self.targets_q = Queue()  # url, name
        await self.targets_q.put((self.url, "index"))
        self.running = True

        tasks = []
        for _ in range(self.task_count):
            tasks.append(asyncio.create_task(self.dump()))
        for t in tasks:
            await t

        self.running = False

    async def dump(self):
        """ 核心下载方法 """
        while self.running:
            # queue.get会一直等待，需要设置超时
            # 但不能使用get_nowait，会变成单任务
            try:
                url, name = await asyncio.wait_for(self.targets_q.get(), 7)
            except Exception as e:
                # self.error_log("Failed to get item form queue.", e=e)
                break
            if url in self.fetched_urls:
                continue
            # 下载保存
            await self.download((url, name))
            self.fetched_urls.append(url)
            # 如果是html则提取链接
            if await self.is_html(url):
                async with aiohttp.ClientSession(
                    connector=self.connector, timeout=self.timeout
                ) as session:
                    try:
                        async with session.get(url, headers=self.headers) as resp:
                            d = pq(await resp.text())
                            # 遍历链接
                            for a in d("a"):
                                txt = pq(a).text()
                                href = pq(a).attr("href")
                                # 没有文字或链接的不要
                                if not txt or not href:
                                    continue
                                href_parsed = urlparse(href)
                                if href_parsed.netloc:
                                    # 不在同一个域下不要
                                    if href_parsed.netloc != self.netloc:
                                        continue
                                if href_parsed.scheme:
                                    # 不是http协议不要
                                    if not href_parsed.scheme.startswith("http"):
                                        continue
                                new_url = urljoin(url, href_parsed.path)
                                fullname = urlparse(new_url).path.lstrip("/")
                                await self.targets_q.put((new_url, fullname))
                                # self.targets_q.put_nowait((new_url, fullname))
                    except Exception as e:
                        msg = "Failed to dump url %s" % url
                        self.error_log(msg=msg, e=e)
                    finally:
                        await session.close()
            if self.targets_q.empty():
                break

    async def is_html(self, url) -> bool:
        """ 判断目标URL是不是属于html页面 """
        async with aiohttp.ClientSession(
            connector=self.connector, timeout=self.timeout
        ) as session:
            try:
                async with session.head(url, headers=self.headers) as resp:
                    return bool("html" in resp.headers.get("content-type", ""))
            except Exception as e:
                msg = "Failed to dump url %s" % url
                self.error_log(msg=msg, e=e)
            finally:
                await session.close()
