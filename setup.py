#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import sys
import setuptools

# 'setup.py publish' shortcut.
if sys.argv[-1] == "publish":
    os.system("rm -rf dist")
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    sys.exit()

here = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(here, "dumpall", "__version__.py"), "r", encoding="utf-8") as f:
    exec(f.read(), about)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    license=about["__license__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    # include_package_data=True,
    test_suite="tests",
    entry_points={"console_scripts": ["dumpall = dumpall:main"]},
    install_requires=["click", "aiohttp", "aiomultiprocess"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Chinese (Simplified)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
        "Topic :: Utilities",
    ],
)
