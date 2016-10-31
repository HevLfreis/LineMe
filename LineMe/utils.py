#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/10/26
# Time: 19:09
import hashlib

from LineMe.settings import DEPLOYED_LANGUAGE


def get_template_dir(appname):
    lang = DEPLOYED_LANGUAGE
    if lang == 'zh-cn':
        return appname + '/zh_cn/'
    else:
        return appname + '/us_en/'


def logger_join(*args, **kwargs):
    if not args:
        return ''
    else:
        str_arg = ' '.join([str(arg) for arg in args])
        if not kwargs:
            return str_arg
        else:
            return str_arg + ' ' + ' '.join([k.upper()+':'+str(v) for k, v in kwargs.items()])


def md5(s):
    if type(s) is str or unicode:
        m = hashlib.md5()
        m.update(s)
        return m.hexdigest()
    else:
        return ''
