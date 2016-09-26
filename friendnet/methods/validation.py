#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/11
# Time: 13:45
import re

from django.contrib.auth.models import User

from friendnet.models import Group, GroupMember
from LineMe.constants import CITIES_TABLE, IDENTIFIER, LINK_BONUS


def validate_username(name):
    if re.match("^[a-zA-Z][a-zA-Z0-9]{5,20}$", name):
        return True
    return False


def validate_username_exist(name):
    if validate_username(name):
        if not User.objects.filter(username=name).exists():
            return True
    return False


def validate_email(email):
    if not User.objects.filter(email=email).exists():
        if re.match("^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9]"
                    "(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9]"
                    "(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$", email):
            return True
    return False


def validate_passwd(password, password2):
    if re.match("^[a-zA-Z0-9]{6,20}$", password):
        if password == password2:
            return True
    return False


def validate_group_info(name, identifier, gtype):
    if re.match("^[a-zA-Z][a-zA-Z0-9\s]{2,20}$", name):
        if not Group.objects.filter(group_name=name).exists():
            if identifier in IDENTIFIER:
                if gtype == 0 or gtype == 1:
                    return True
    return False


def check_groupid(user, groupid):
    if groupid is None:
        return -2
    elif Group.objects.filter(id=groupid).exists() and \
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
