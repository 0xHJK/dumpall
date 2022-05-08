#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author: HJK
@file: dumper
@time: 2019-10-23
"""

import os
from pydoc import cli
import random
import traceback
import click
import aiohttp
from tempfile import NamedTemporaryFile
from urllib.parse import unquote
from aiohttp_proxy import ProxyConnector


class BaseDumper(object):
    """ 基本下载类 其他Dumper继承BaseDumper """

    def __init__(self, url: str, outdir: str, **kwargs):
        self.url = url
        self.outdir = outdir
        self.proxy = kwargs.get("proxy", "")
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.force = bool(kwargs.get("force", False))
        self.debug = bool(kwargs.get("debug", False))
        self.targets = []

        # load useragents
        self.useragents = [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41"
        ]
        try:
            ua_txt = os.path.join(
                os.path.dirname(__file__), "data", "user-agents-from-seclists.txt"
            )
            with open(ua_txt, "r") as f:
                self.useragents = f.readlines()
        except Exception as e:
            msg = "Failed to set random user-agent %s" % (ua_txt)
            self.error_log(msg=msg, e=e)

    @property
    def headers(self):
        return {"User-Agent": random.choice(self.useragents).strip()}

    @property
    def connector(self):
        if self.proxy:
            try:
                _connector = ProxyConnector.from_url(
                    self.proxy, verify_ssl=False, rdns=True
                )
            except Exception as e:
                msg = (
                    "Failed to set proxy %s\neg. socks5://[user:pass@]127.0.0.1:1080"
                    % (self.proxy)
                )
                self.error_log(msg=msg, e=e)
                exit(-1)
        else:
            _connector = aiohttp.TCPConnector(verify_ssl=False)  # 默认禁用证书验证
        return _connector

    def convert(self, data: bytes) -> bytes:
        """ 处理数据 """
        return data

    def makedirs(self, fullname):
        """ 根据URL文件名创建文件夹 """
        outdir = os.path.dirname(fullname)
        if outdir:
            if os.path.isfile(outdir):
                # 如果之前已经作为文件写入了，则需要删除
                click.secho("%s is a file. It will be removed." % outdir, fg="yellow")
                os.remove(outdir)
            if not os.path.exists(outdir):
                try:
                    os.makedirs(outdir)
                except Exception as e:
                    # TODO: 存在异步创建文件夹冲突问题
                    msg = "Failed to makedirs %s" % (fullname)
                    self.error_log(msg=msg, e=e)

    def error_log(self, msg: str, e: Exception = None):
        """ 统一错误日志 """
        click.secho(msg, fg="red")
        if e:
            click.secho(str(e.args), fg="red")
        if self.debug:
            click.echo(str(traceback.format_exc()))

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
        filename = unquote(filename)
        fullname = os.path.abspath(os.path.join(self.outdir, filename))
        self.makedirs(fullname=fullname)

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
            msg = "Failed to download file %s %s" % (url, filename)
            self.error_log(msg=msg, e=e)

    async def fetch(self, url: str, times: int = 3) -> tuple:
        """ 从URL获取内容，如果失败默认重试三次 """
        # TODO：下载大文件需要优化
        async with aiohttp.ClientSession(
            connector=self.connector, timeout=self.timeout
        ) as session:
            try:
                resp = await session.get(url=url, headers=self.headers)
                ret = (resp.status, await resp.content.read())
            except Exception as e:
                if times > 0:
                    return await self.fetch(url, times - 1)
                else:
                    # 获取内容失败
                    msg = "Failed to fetch url %s" % (url)
                    self.error_log(msg=msg, e=e)
                    ret = (0, None)
            finally:
                await session.close()
            return ret

    async def parse(self, url: str):
        """ 从URL下载文件并解析 """
        pass

    async def indexfile(self, url: str) -> NamedTemporaryFile:
        """ 创建一个临时索引文件index/wc.db """
        status, data = await self.fetch(url)
        if not data:
            click.secho("Failed to fetch data [%s] %s" % (status, url), fg="red")
            return
        with NamedTemporaryFile(mode="wb", delete=False) as f:
            f.write(data)
            f.close()
            return f

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
