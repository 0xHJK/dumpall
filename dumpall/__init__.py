#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import os
import sys
import time
import asyncio
import importlib
import traceback
import click
from os import path
from urllib.parse import urlparse

from . import __version__
from .exceptions import UrlError

addons_map = {".git": "dumpgit", ".svn": "dumpsvn", ".DS_Store": "dumpds"}


def banner():
    bn = """
       ___                  ___   __   __ 
      / _ \__ ____ _  ___  / _ | / /  / / 
     / // / // /  ' \/ _ \/ __ |/ /__/ /__
    /____/\_,_/_/_/_/ .__/_/ |_/____/____/
                   /_/                    

    https://github.com/0xHJK/dumpall
    --------------------------------------------- """
    info = "                                       v%s %s\n" % (
        __version__.__version__,
        __version__.__author__,
    )
    click.secho(bn, fg="cyan")
    click.echo(info)


# def usage():
#     msg = "Usage: %s <url>" % sys.argv[0]
#     example = """
# Example:
#     dumpall http://example.com/.git
#     dumpall http://example.com/.svn
#     dumpall http://example.com/.DS_Store
# """
#     click.secho(msg, fg="red")
#     click.echo(example)


def start(url, outdir):
    for k, v in addons_map.items():
        if k in url:
            try:
                if not path.exists(outdir):
                    os.makedirs(outdir)
                addon = importlib.import_module(".addons." + v, __package__)
                dumper = addon.Dumper(url, outdir)
                asyncio.run(dumper.start())
            except Exception as e:
                print(e.args)
                err = traceback.format_exc()
                print(err)
            finally:
                break
    else:
        raise UrlError("URL不符合要求，请参考示例说明")


@click.command()
@click.version_option()
@click.option("-u", "--url", help="指定目标URL，支持.git/.svn/.DS_Store")
@click.option("-o", "--outdir", help="指定保存目录，默认目录名为主机名")
def main(url, outdir):
    """
    信息泄漏利用工具，适用于.git/.svn/.DS_Store

    Example: dumpall -u http://example.com/.git
    """
    banner()

    # 如果没有URL参数则要求输入
    if not url or "//" not in url:
        url = click.prompt("请输入目标URL，必须包含http或https\n >>")

    if not outdir:
        url_obj = urlparse(url)
        outdir = "%s_%s" % (url_obj.hostname, url_obj.port)
    # tm = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
    # outdir = "%s_%s" % (hostname, tm)

    click.secho("Target: %s" % url, fg="yellow")
    click.secho("Output Directory: %s\n" % outdir, fg="yellow")

    start(url, outdir)
