# Dump all: 多种泄漏格式 一种解决方式

![Dump all](https://github.com/0xHJK/dumpall/raw/master/static/dumpall.png)

> ⚠️ 警告：仅用于学习或已授权的测试，禁止用于非法用途，否则后果自负。

> ⚠️ WARNING: For study or authorized testing only. Prohibit the illegal use, or at your peril.

[Dumpall](https://github.com/0xHJK/dumpall) 是一款信息泄漏/源代码泄漏利用工具，适用于以下场景：

- [x] `.git`源代码泄漏
- [x] `.svn`源代码泄漏
- [x] `.DS_Store`信息泄漏

特点
- 支持多种泄漏情况利用
- 基于Python3，使用asyncio异步处理
- 请求失败时自动重发请求
- 多进程+多协程，速度超快

项目地址：<https://github.com/0xHJK/dumpall>

> 在macOS下的Python 3.7中测试通过，建议使用Python 3.7+
>
> 后续考虑增加其他常见的信息泄漏利用，如开发工具或服务器的配置文件等

## Quickstart

```bash
# pip安装
pip install dumpall
# 查看版本
dumpall --version
```

```bash
# 手动下载使用
git clone https://github.com/0xHJK/dumpall
cd dumpall
查看版本
python3 dumpall.py --version
```

```bash
# 下载文件（源代码）
dumpall -u <url> [-o <outdir>]

# 示例
dumpall -u http://example.com/.git/
dumpall -u http://example.com/.svn/
dumpall -u http://example.com/.DS_Store
```

参数说明

```bash
Options:
  --version          Show the version and exit.
  -u, --url TEXT     指定目标URL，支持.git/.svn/.DS_Store
  -o, --outdir TEXT  指定保存目录，默认目录名为主机名
  --help             Show this message and exit.
```

`.git`源代码泄漏利用

![0xHJK dumpall gitdumper](https://github.com/0xHJK/dumpall/raw/master/static/gitdumper.png)

`.svn`源代码泄漏利用

![0xHJK dumpall svndumper](https://github.com/0xHJK/dumpall/raw/master/static/svndumper.png)

`.DS_Store`信息泄漏利用

![0xHJK dumpall dsdumper](https://github.com/0xHJK/dumpall/raw/master/static/dsdumper.png)

## CHANGELOG

- 2019-10-27 v0.2.0
  - 优化下载方法
  - 完成`.DS_Store`信息泄漏利用功能
- 2019-10-24 v0.1.0
  - 项目架构优化
  - 完成`.svn`源代码泄漏利用功能
- 2019-10-23
  - 完成`.git`源代码泄漏利用功能
- 2019-10-19 项目启动

## Credit

本项目参考或使用了以下项目，在此感谢相关开发者

- https://github.com/lijiejie/GitHack
- https://github.com/admintony/svnExploit
- https://github.com/sbp/gin
- https://github.com/gehaxelt/Python-dsstore
- https://github.com/aio-libs/aiohttp
- https://github.com/jreese/aiomultiprocess
- https://github.com/pallets/click