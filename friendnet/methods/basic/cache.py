#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/9/30
# Time: 10:24
from django.core.cache import cache
import networkx as nx


def get_or_set_d(kw, func, user, groupid):
    kw = kw + str(user.id) + str(groupid)
    data = cache.get(kw)
    if not data:
        data = func(user, groupid)
        cache.set(kw, data)

    return data


def test():
    G = nx.Graph()
    cache.set('test', G)
    print 'test ', cache.get('test') is None


def get_or_set(kw):
    def decorator(func):
        def wrapper(*args, **kwargs):
            arg = '-'.join(map(str, args))
            key = kw + '-' + arg
            data = cache.get(key)
            if not data:
                # print key, 'notin'
                data = func(*args, **kwargs)
                cache.set(key, data)
            # else:
            #     print key, 'bingo'
            return data
        return wrapper
    return decorator
