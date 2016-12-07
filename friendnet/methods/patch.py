#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/12/7
# Time: 13:50
from friendnet.models import Link


def smu(groupid, link, n):
    return limited_friends(groupid, link, n)


def limited_friends(groupid, link, n):
    if link.group.id != groupid:
        return False

    if Link.objects.filter(creator=link.creator, status=3).count() >= n:
        return True
    return False
