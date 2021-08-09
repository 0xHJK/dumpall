#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author: HJK
@file: dumper
@time: 2019-10-23
"""

import os
import click
import aiohttp
from tempfile import NamedTemporaryFile


class BasicDumper(object):
    """ 基本下载类 """

    def __init__(self, url: str, outdir: str, force: False):
        self.url = url
        self.outdir = outdir
        self.force = force
        self.targets = []
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41"
        }

    async def start(self):
        """ 入口方法 """
        await self.dump()

    async def dump(self):
        """ DUMP核心方法，解析索引，创建任务池，调用download """
        pass

    async def download(self, target: tuple):
        """ 下载任务（协程） """
        url, filename = target

        # 创建目标目录（filename可能包含部分目录）
        fullname = os.path.abspath(os.path.join(self.outdir, filename))
        outdir = os.path.dirname(fullname)
        if outdir:
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            elif os.path.isfile(outdir):
                # 如果之前已经作为文件写入了，则需要删除
                click.secho("%s is a file. It will be removed." % outdir, fg="yellow")
                os.remove(outdir)
                os.makedirs(outdir)

        # 获取数据
        status, data = await self.fetch(url)
        if status != 200 or data is None:
            # None才代表出错，data可能为b""
            click.secho("[%s] %s %s" % (status, url, filename), fg="red")
            return

        click.secho("[%s] %s %s" % (status, url, filename), fg="green")

        # 处理数据（如有必要）
        data = self.convert(data)

        # 保存数据
        try:
            with open(fullname, "wb") as f:
                f.write(data)
        except IsADirectoryError:
            # 多协程/线程/进程下，属于正常情况
            pass
        except Exception as e:
            click.secho("[Failed] %s %s" % (url, filename), fg="red")
            click.secho(str(e.args), fg="red")

    def convert(self, data: bytes) -> bytes:
        """ 处理数据 """
        return data

    async def fetch(self, url: str, times: int = 3) -> tuple:
        """ 从URL获取内容，如果失败默认重试三次 """
        # TODO：下载大文件需要优化
        async with aiohttp.ClientSession() as session:
            try:
                resp = await session.get(url, headers=self.headers)
                ret = (resp.status, await resp.content.read())
            except Exception as e:
                if times > 0:
                    return await self.fetch(url, times - 1)
                else:
                    # 获取内容失败
                    click.secho("Failed %s" % (url), fg="red")
                    click.secho(str(e.args), fg="red")
                    ret = (0, None)
            return ret

    async def parse(self, url: str):
        """ 从URL下载文件并解析 """
        pass

    async def indexfile(self, url: str) -> NamedTemporaryFile:
        """ 创建一个临时索引文件index/wc.db """
        idxfile = NamedTemporaryFile()
        status, data = await self.fetch(url)
        if not data:
            click.secho("Failed [%s] %s" % (status, url), fg="red")
            return
        with open(idxfile.name, "wb") as f:
            f.write(data)
        return idxfile

    async def checkit(self, url: str, filename: str) -> bool:
        # 修复任意位置存储的漏洞
        # https://drivertom.blogspot.com/2021/08/git.html
        fullname = os.path.abspath(os.path.join(self.outdir, filename))
        if not fullname.startswith(self.outdir):
            # 如果文件超出目标位置范围
            click.secho(
                f"[WARNING] THIS MAY BE A HONEYPOT !!! \n[URL]: {url}\n[FILENAME]: {filename}\n",
                fg="red",
            )
            try:
                self.force = click.confirm("Do you want to continue?", abort=True)
            except Exception as e:
                click.secho("Abort.", fg="yellow")
            return self.force
        return True
