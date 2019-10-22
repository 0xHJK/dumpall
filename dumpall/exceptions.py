#!/usr/bin/env python3
# -*- coding=utf-8 -*-


class UrlError(RuntimeError):
    """ URL不符合要求 """

    def __init__(self, *args, **kwargs):
        pass


class IndexError(RuntimeError):
    """ 未找到索引文件，如.git/index，.svn/entries, .DS_Store """

    def __init__(self, *args, **kwargs):
        pass
