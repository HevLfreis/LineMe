#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/6/12 
# Time: 19:16
#

from django.template.defaulttags import register


@register.filter
def get_value(dictionary, key):
    return dictionary.get(key)
