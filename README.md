# Dump all

一个信息泄漏聚合下载工具，适用于以下场景：

- [x] `.git`信息泄漏
- [ ] `.svn`信息泄漏
- [ ] `.DS_Store`信息泄漏

> 项目正在开发中，开发环境为Python3.7

## Quickstart

```bash
# 安装
pip install dumpall

# 下载文件
dumpall -u <url> [-o <outdir>]

# 示例
dumpall -u http://example.com/.git/
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
- https://github.com/sbp/gin
- https://github.com/aio-libs/aiohttp
- https://github.com/jreese/aiomultiprocess
- https://github.com/pallets/click