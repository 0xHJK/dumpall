# Dump all

[dumpall](https://github.com/0xHJK/dumpall)是一款信息泄漏/源代码泄漏利用工具，适用于以下场景：

- [x] `.git`源代码泄漏
- [x] `.svn`源代码泄漏
- [ ] `.DS_Store`信息泄漏

特点
- 支持多种泄漏情况利用
- 请求失败时自动重发请求
- 基于Python3，使用asyncio
- 多进程+多协程，速度超快

> 在macOS下的Python 3.7中测试通过，建议使用Python 3.7+

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

## Credit

本项目参考或使用了以下项目，在此感谢相关开发者

- https://github.com/lijiejie/GitHack
- https://github.com/admintony/svnExploit
- https://github.com/sbp/gin
- https://github.com/aio-libs/aiohttp
- https://github.com/jreese/aiomultiprocess
- https://github.com/pallets/click