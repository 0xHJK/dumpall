#!/usr/bin/env python3
# -*- coding=utf-8 -*-

"""
SVN源代码泄露利用工具
"""

import re
from ..dumper import BasicDumper

class Dumper(BasicDumper):
    def __init__(self, url, outdir):
        super(Dumper, self).__init__(url, outdir)
        self.base_url = re.sub(".svn.*", ".svn", url)

    async def start(self):
        """ dumper入口方法 """
        pass