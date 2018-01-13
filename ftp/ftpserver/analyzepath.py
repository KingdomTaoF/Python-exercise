#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-12-27 15:13:51

import re


def analyzePath(self, pathstring):

    # def  __init__(self):
        self.current_dir = '/var/ftp/pub/tt'
        self.userinfo

    reobj_root = re.compile('^/')
    # reobj_back = re.compile('^\.')
    if reobj_root.match(pathstring):
        if pathstring.startswith(self.userinfo['home_dir']):
            return ['203', pathstring]
        else:
            return ['403', '%s 是非法路径']
    # elif reobj_back.match(pathstring):
    else:
        abs_path_list = self.current_dir.split('/')
        path_list = pathstring.split('/')
        for i in path_list:
            if i == '..':
                path_list.pop(0)
                abs_path_list.pop(-1)
            elif i == '.':
                path_list.pop(0)
            else:
                continue
        abs_path = '%s/%s' % ('/'.join(abs_path_list), '/'.join(path_list))
        return ['203', abs_path]
        # print('生成的路径为：%s' % abs_path)
