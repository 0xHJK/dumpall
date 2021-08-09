#!/usr/bin/env python3
# -*- coding=utf-8 -*-

"""
    适用于开启index页面的网站，如apache index
"""

import asyncio
import aiohttp
import click
from urllib.parse import urlparse, urljoin
from asyncio.queues import Queue
from pyquery import PyQuery as pq
from ..dumper import BasicDumper


class Dumper(BasicDumper):
    """ index dumper """

    def __init__(self, url: str, outdir: str, force=False):
        super(Dumper, self).__init__(url, outdir, force)
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
        for i in range(self.task_count):
            tasks.append(asyncio.create_task(self.dump()))
        for t in tasks:
            await t

    async def dump(self):
        """ 核心下载方法 """
        while self.running:
            url, name = await self.targets_q.get()
            if url in self.fetched_urls:
                continue
            try:
                if await self.is_html(url):
                    # 如果是html则提取链接
                    async with aiohttp.ClientSession(
                        connector=aiohttp.TCPConnector(verify_ssl=False)
                    ) as session:
                        async with session.get(url, headers=self.headers) as resp:
                            d = pq(await resp.text())
                            # 遍历链接
                            for a in d("a"):
                                txt = pq(a).text()
                                href = pq(a).attr("href")
                                href_parsed = urlparse(href)
                                if not txt:  # 没有文字的不要
                                    continue
                                if href_parsed.netloc:
                                    if href_parsed.netloc != self.netloc:  # 不在同一个域下不要
                                        continue
                                if href_parsed.scheme:
                                    if not href_parsed.scheme.startswith(
                                        "http"
                                    ):  # 不是http协议不要
                                        continue
                                new_url = urljoin(url, href_parsed.path)
                                fullname = urlparse(new_url).path.lstrip("/")
                                await self.targets_q.put((new_url, fullname))
                else:
                    # 如果不是html则下载保存
                    await self.download((url, name))
                self.fetched_urls.append(url)
            except Exception as e:
                click.secho("Dump %s failed" % url, fg="red")
                print(e)
            if self.targets_q.empty():
                break

    async def is_html(self, url) -> bool:
        """ 判断目标URL是不是属于html页面 """
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
        ) as session:
            async with session.head(url, headers=self.headers) as resp:
                return bool("html" in resp.headers.get("content-type", ""))
