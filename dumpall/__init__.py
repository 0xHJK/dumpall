#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import os
import asyncio
import importlib
import traceback
import click
from os import path
from urllib.parse import urlparse
from .__version__ import __version__, __author__

addons_map = {".git": "gitdumper", ".svn": "svndumper", ".DS_Store": "dsdumper"}


def banner():
    bn = """
       ___                  ___   __   __ 
      / _ \__ ____ _  ___  / _ | / /  / / 
     / // / // /  ' \/ _ \/ __ |/ /__/ /__
    /____/\_,_/_/_/_/ .__/_/ |_/____/____/
                   /_/                    

    https://github.com/0xHJK/dumpall
    --------------------------------------------- """
    info = "                                       v%s %s\n" % (__version__, __author__)
    click.secho(bn, fg="cyan")
    click.echo(info)


def start(url: str, outdir: str, proxy: str, force: bool, debug: bool):
    for k, v in addons_map.items():
        if k in url:
            addon = importlib.import_module(".addons." + v, __package__)
            break
    else:
        # click.secho("URL不符合要求", fg="red")
        addon = importlib.import_module(".addons.idxdumper", __package__)
    click.secho("Module: %s\n" % addon.__name__, fg="yellow")
    try:
        dumper = addon.Dumper(url, outdir, proxy=proxy, force=force, debug=debug)
        asyncio.run(dumper.start())
    except KeyboardInterrupt as e:
        click.secho("Exit.", fg="magenta")
        exit()
    except Exception as e:
        click.secho(str(e.args), fg="red")
        click.echo(str(traceback.format_exc()))


@click.command()
@click.version_option()
@click.option("-u", "--url", help="指定目标URL，支持.git/.svn/.DS_Store，以及类index页面")
@click.option("-o", "--outdir", default="", help="指定下载目录，默认目录名为主机名")
@click.option(
    "-p", "--proxy", default="", help="指定代理 scheme://[user:pass@]hostname:port"
)
@click.option("-f", "--force", is_flag=True, help="强制下载（可能会有蜜罐风险）")
@click.option("-d", "--debug", is_flag=True, help="调试模式 输出更多日志")
def main(
    url,
    outdir,
    proxy,
    force,
    debug,
):
    """
    信息泄漏利用工具，适用于.git/.svn/.DS_Store，以及目录列出下载

    Example: dumpall -u http://example.com/.git
    """
    banner()

    # 如果没有URL参数则要求输入
    if not url or "//" not in url:
        url = click.prompt("请输入目标URL，必须包含http://或https://\n >>")

    # 合成并创建下载目录
    url_obj = urlparse(url)
    outdir = path.join(outdir, "%s_%s" % (url_obj.hostname, url_obj.port))
    basedir = outdir
    i = 1
    while path.exists(outdir):
        outdir = "%s_%s" % (basedir, i)
        i += 1
    outdir = path.abspath(outdir)
    os.makedirs(outdir)

    click.secho("Target: %s" % url, fg="yellow")
    click.secho("Output Directory: %s\n" % outdir, fg="yellow")

    # fix Error: Too many open files
    try:
        os.system("ulimit -n 65535")
    except Exception as e:
        click.secho("请手动修改打开文件数量限制")
        pass

    start(url, outdir, proxy=proxy, force=force, debug=debug)
