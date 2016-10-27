#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/10/26
# Time: 19:05
import re

from django.contrib.auth.models import User
from friendnet.models import Group

from LineMe.constants import IDENTIFIER


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


def validate_email_for_reset(email):
    if User.objects.filter(email=email).exists():
        if re.match("^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9]"
                    "(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9]"
                    "(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$", email):
            return True
    return False


def validate_passwd(password, password2):
    if password and password2:
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
