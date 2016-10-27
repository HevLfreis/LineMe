#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/11
# Time: 13:45

from LineMe.constants import LINK_BONUS
from friendnet.models import Group, GroupMember


def check_groupid(user, groupid):
    if groupid is None:
        return -2
    elif Group.objects.filter(id=groupid, deprecated=False).exists() and \
            GroupMember.objects.filter(
                group__id=groupid,
                user=user
            ).exists():

        return groupid
    else:
        return 0


def check_credits(user, bonus=''):
    if bonus == 'bonus':
        if user.extra.credits > 9999:
            return
    elif bonus == 'punish':
        if user.extra.credits < LINK_BONUS:
            return
    else:
        return
