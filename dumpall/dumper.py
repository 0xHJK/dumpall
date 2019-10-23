#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author: HJK
@file: dumper
@time: 2019-10-23
"""

import click
import aiohttp

class BasicDumper(object):
    """ 基本下载类 """
    def __init__(self, url, outdir):
        self.url = url
        self.outdir = outdir
        self.targets = []
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41"
        }

    async def start(self):
        """ 入口方法 """
        pass

    async def parse(self, url):
        """ 从URL下载文件并解析 """
        pass

    async def dump_task(self):
        """ 创建目录、调用fetch、保存文件 """
        pass

    async def fetch(self, url):
        """ 从URL获取内容 """
        async with aiohttp.request("GET", url, headers=self.headers) as resp:
            if resp.status == 200:
                try:
                    return await resp.content.read()
                except Exception as e:
                    # 获取内容失败
                    click.secho("Failed [%s] %s" % (resp.status, url), fg="red")
                    click.secho(e.args, fg="red")
            else:
                # 请求状态异常
                click.secho("Failed [%s] %s" % (resp.status, url), fg="red")
                return None


