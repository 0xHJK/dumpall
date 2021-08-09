#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import re
import zlib
import click
from os import path
from aiomultiprocess import Pool
from ..dumper import BasicDumper
from ..thirdparty.gin import parse


class Dumper(BasicDumper):
    def __init__(self, url: str, outdir: str, force=False):
        super(Dumper, self).__init__(url, outdir, force)
        self.base_url = re.sub(".git.*", ".git", url)

    async def start(self):
        """ 入口方法 """
        await self.dump()

    async def dump(self):
        """ .git DUMP核心方法，解析索引，创建进程池，调用download """
        # 创建一个临时文件来存储index
        idxfile = await self.indexfile(self.base_url + "/index")
        # 从index中获取文件hash和路径
        for entry in parse(idxfile.name):
            if "sha1" in entry.keys():
                sha1 = entry.get("sha1", "").strip()
                filename = entry.get("name", "").strip()
                if not sha1 or not filename:
                    continue
                url = "%s/objects/%s/%s" % (self.base_url, sha1[:2], sha1[2:])
                if not self.force and not await self.checkit(url, filename):
                    exit()
                self.targets.append((url, filename))
        idxfile.close()
        # 创建进程池，调用download
        async with Pool() as pool:
            await pool.map(self.download, self.targets)

    def convert(self, data: bytes) -> bytes:
        """ 用zlib对数据进行解压 """
        if data:
            try:
                data = zlib.decompress(data)
                # Bytes正则匹配
                data = re.sub(rb"blob \d+\x00", b"", data)
            except Exception as e:
                click.secho(str(e.args), fg="red")
        return data
