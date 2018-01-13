#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-12-28 15:23:23

import os


def getDirSize(dir_path):
    size = 0
    for dirpaths, dirnames, filenames in os.walk(dir_path):
        for f in filenames:
            size += os.path.getsize(os.path.join(dirpaths, f))
    return size


print(getDirSize('/var/ftp/pub/tt'))
