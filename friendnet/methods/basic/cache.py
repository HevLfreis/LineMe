#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/9/30
# Time: 10:24
from django.core.cache import cache


def get_or_set(kw, func, user, groupid):
    kw = kw + str(user.id) + str(groupid)
    data = cache.get(kw)
    if not data:
        data = func(user, groupid)
        cache.set(kw, data)

    return data
