#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author: HJK
@file: dumper
@time: 2019-10-23
"""

import os
import random
from tempfile import NamedTemporaryFile
from urllib.parse import unquote
import aiohttp
from aiohttp_proxy import ProxyConnector
import click



class RHB(object):
    """ 请求的head和body"""
    def __init__(self,url:str,proxy:str,random_agent:bool):
        super().__init__()
        self.url=url
        self.proxy=proxy
        self.useragents=[
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41',
        ]
        """随机ua来自项目user-agent"""
        with open(os.path.abspath(os.path.dirname(__file__))+"/data/user-agents-from-seclists.txt") as f:
            self.useragents = (f.read().split("\n"))
        self.useragent={
            "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41'
        }
        self.random_agent = random_agent
            
class BasicDumper(object):
    

    def __init__(self, rhb: RHB, outdir: str, force: False):
        self.rhb = rhb
        self.outdir = outdir
        self.force = force
        self.targets = []
        
        

    async def start(self):
        """ 入口方法 """
        await self.dump()

    async def dump(self):
        """ DUMP核心方法，解析索引，创建任务池，调用download """
        pass

    async def download(self, target: tuple):
        """ 下载任务（协程） """
        url, filename = target
        filename = unquote(filename)
        # 创建目标目录（filename可能包含部分目录）
        fullname = os.path.abspath(os.path.join(self.outdir, filename))
        outdir = os.path.dirname(fullname)
        if outdir:
            """修复异步创建文件夹时，执行报错，就是判断的时候文件夹不存在，但是创建的时候，文件夹被其他协程创建了"""
            """尝试加过锁，但是好像没效果不知道是否有更好的修复方法"""
            if not os.path.exists(outdir):
                try:
                    os.makedirs(outdir)
                except FileExistsError:
                    print("异步创建文件异常")
                    pass
            elif os.path.isfile(outdir):
                # 如果之前已经作为文件写入了，则需要删除
                click.secho("%s is a file. It will be removed." % outdir, fg="yellow")
                os.remove(outdir)
                try:
                    os.makedirs(outdir)
                except FileExistsError:
                    print("异步创建文件异常")
                    pass

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
    def getConnection(self):
        connector= aiohttp.TCPConnector(verify_ssl=False)  # 默认禁用证书验证
        if self.rhb.proxy: # 存在代理，则用代理的
            try:
                # connector = ProxyConnector(rdns=True).from_url(self.rhb.proxy)
                # connector._ssl=False # 调试得知用此两行替换下一行也可行得通
                connector = ProxyConnector().from_url(self.rhb.proxy,verify_ssl=False,rdns=True)
                # 此处代码调试了很久，from_url方法会解析传入的代理地址，然后传入构造方法，并返回新对象。导致ProxyConnector(verify_ssl=False,rdns=True)中传入的参数无效。
            except Exception as e:
                print("代理异常，请检查代理格式!!!")
                print("socks5://user:pass@127.0.0.1:1080")
                print("socks5://127.0.0.1:1080")
                print("socks4://127.0.0.1:9050")
                print("http://127.0.0.1:8080")     
                exit() # 退出
        return connector
    def convert(self, data: bytes) -> bytes:
        """ 处理数据 """
        return data
    
    async def fetch(self, url: str, times: int = 3) -> tuple:
        """ 从URL获取内容，如果失败默认重试三次 """
        # TODO：下载大文件需要优化
        connector=self.getConnection()
        
        async with aiohttp.ClientSession(connector=connector) as session:
            try:
                useragent = self.rhb.useragent
                if self.rhb.random_agent==True:
                    useragent= {"User-Agent":random.choice(self.rhb.useragents)}
                resp = await session.get(url=url,headers=useragent)
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
        status, data = await self.fetch(url)
        if not data:
            click.secho("Failed [%s] %s" % (status, url), fg="red")
            return
        with NamedTemporaryFile(mode="wb",delete=False) as f:
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
