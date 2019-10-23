#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import re
import os
import zlib
import click
import aiohttp
from tempfile import NamedTemporaryFile
from aiomultiprocess import Pool
from ..thirdparty.gin import parse


class Dumper(object):
    def __init__(self, url, outdir):
        self.base_url = re.sub(".git.*", ".git", url)
        self.outdir = outdir
        self.urls = []

    async def start(self):
        """ 入口方法 """
        index_url = self.base_url + "/index"
        # 创建一个临时文件
        tmpfile = NamedTemporaryFile()
        await self.fetch(index_url, tmpfile.name)
        # 从index中获取文件hash和路径
        for entry in parse(tmpfile.name):
            if "sha1" in entry.keys():
                sha1 = entry.get("sha1", "").strip()
                filename = entry.get("name", "").strip()
                if not sha1 or not filename:
                    continue
                url = "%s/objects/%s/%s" % (self.base_url, sha1[:2], sha1[2:])
                self.urls.append((url, filename))
        tmpfile.close()

        await self.dump()

    async def dump(self):
        """ 使用map调用dump_task """
        async with Pool() as pool:
            await pool.map(self.dump_task, self.urls)

    async def dump_task(self, args):
        """ 创建目录并调用fetch """
        url, filename = args
        click.echo("%s %s" % (url, filename))
        fullname = os.path.join(self.outdir, filename)
        outdir = os.path.dirname(fullname)
        # 创建目标目录（filename可能包含部分目录）
        if outdir and not os.path.exists(outdir):
            os.makedirs(outdir)
        await self.fetch(url, fullname)

    async def fetch(self, url, filename):
        """ 从URL获取内容保存到文件 """
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41"
        }
        async with aiohttp.request("GET", url, headers=headers) as resp:
            if resp.status == 200:
                try:
                    # 保存文件
                    with open(filename, "wb") as f:
                        data = await resp.content.read()
                        try:
                            data = zlib.decompress(data)
                            # Bytes正则匹配
                            data = re.sub(b"blob \d+\x00", b"", data)
                        except:
                            # index文件不需要解压
                            pass
                        f.write(data)
                except Exception as e:
                    click.secho("Failed [%s] %s" % (resp.status, url), fg="red")
                    click.secho(e.args, fg="red")
            else:
                click.secho("Failed [%s] %s" % (resp.status, url), fg="red")
