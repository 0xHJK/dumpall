# Dump all: 多种泄漏形式，一种利用方式

<p align="center">
  <a href="https://github.com/0xHJK/dumpall">
    <img src="https://github.com/0xHJK/dumpall/raw/master/static/dumpall.png" alt="dumpall">
  </a>
  <span>dumpall 是一款信息泄漏/源代码泄漏利用工具</span><br>
<p>

<p align="center">
  <a><img src="https://img.shields.io/pypi/pyversions/dumpall.svg"></a>
  <a href="https://github.com/0xHJK/dumpall/releases">
    <img src="https://img.shields.io/github/v/release/0xHJK/dumpall?include_prereleases">
  </a>
  <a><img src="https://img.shields.io/github/license/0xHJK/dumpall"></a>
</p>

<p align="center">
  <a href="https://github.com/0xHJK/dumpall">https://github.com/0xHJK/dumpall</a>
</p>

<hr>

> ⚠️ **警告：本工具仅用于授权测试，不得用于非法用途，否则后果自负！**
> 
> ⚠️ **WARNING：FOR LEGAL PURPOSES ONLY!**


## 🤘 Features

- 支持多种泄漏情况利用
- Dumpall使用方式简单
- 使用asyncio异步处理速度快

适用于以下场景：

- [x] `.git`源代码泄漏
- [x] `.svn`源代码泄漏
- [x] `.DS_Store`信息泄漏
- [x] 目录列出信息泄漏

TODO:

- [ ] 支持更多利用方式
- [ ] 优化大文件下载
- [ ] 优化多任务调度
- [ ] 增强绕过功能

项目地址：<https://github.com/0xHJK/dumpall>

> 在macOS下的Python 3.7中测试通过，建议使用Python 3.7+


## 🚀 QuickStart

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
# 查看版本
python3 dumpall.py --version
```

## 💫 Usage

```bash
# 下载文件（源代码）
dumpall -u <url> [-o <outdir>]

# 示例
dumpall -u http://example.com/.git/
dumpall -u http://example.com/.svn/
dumpall -u http://example.com/.DS_Store
dumpall -u http://example.com/
```

帮助

```bash
$ dumpall --help
Usage: dumpall [OPTIONS]

  信息泄漏利用工具，适用于.git/.svn/.DS_Store，以及index页面

  Example: dumpall -u http://example.com/.git

Options:
  --version          Show the version and exit.
  -u, --url TEXT     指定目标URL，支持.git/.svn/.DS_Store，以及类index页面
  -o, --outdir TEXT  指定下载目录，默认目录名为主机名
  -f, --force        强制下载（可能会有蜜罐风险）
  --help             Show this message and exit.
```

`.git`源代码泄漏利用

![0xHJK dumpall gitdumper](https://github.com/0xHJK/dumpall/raw/master/static/gitdumper.png)

`.svn`源代码泄漏利用

![0xHJK dumpall svndumper](https://github.com/0xHJK/dumpall/raw/master/static/svndumper.png)

`.DS_Store`信息泄漏利用

![0xHJK dumpall dsdumper](https://github.com/0xHJK/dumpall/raw/master/static/dsdumper.png)

## 📜 History

- 2021-08-09 v0.3.1
  - 修复任意位置存储漏洞、增加蜜罐警告
- 2020-05-22 v0.3.0
  - 完成目录列出信息泄漏利用功能
- 2019-10-27 v0.2.0
  - 优化下载方法
  - 完成`.DS_Store`信息泄漏利用功能
- 2019-10-24 v0.1.0
  - 项目架构优化
  - 完成`.svn`源代码泄漏利用功能
- 2019-10-23
  - 完成`.git`源代码泄漏利用功能
- 2019-10-19 项目启动

## 🤝 Credit

本项目参考或使用了以下项目，在此感谢相关开发者

- https://github.com/lijiejie/GitHack
- https://github.com/admintony/svnExploit
- https://github.com/sbp/gin
- https://github.com/gehaxelt/Python-dsstore
- https://github.com/aio-libs/aiohttp
- https://github.com/jreese/aiomultiprocess
- https://github.com/pallets/click

## 📄 License

[MIT License](https://github.com/0xHJK/TotalPass/blob/master/LICENSE)
