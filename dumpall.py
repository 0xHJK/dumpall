#!/usr/bin/env python3
# -*- coding=utf-8 -*-

"""
python3 dumpall.py <url>
"""


import os, sys

_srcdir = "%s/" % os.path.dirname(os.path.realpath(__file__))
_filepath = os.path.dirname(sys.argv[0])
sys.path.insert(1, os.path.join(_filepath, _srcdir))

if sys.version_info[0] == 3:
    import dumpall

    if __name__ == "__main__":
        dumpall.main()
else:  # Python 2
    print("Python3 Only.")
