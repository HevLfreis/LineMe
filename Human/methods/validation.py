#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/11
# Time: 13:45
import re

from django.contrib.auth.models import User

from Human.models import Group, GroupMember
from LineMe.constants import CITIES_TABLE, IDENTIFIER, LINK_BONUS


def validate_username(name):
    if re.match("^[a-zA-Z][a-zA-Z0-9]{5,20}$", name):
        return True
    return False


def validate_username_exist(name):
    if re.match("^[a-zA-Z][a-zA-Z0-9]{5,20}$", name):
        if not User.objects.filter(username=name).exists():
            return True
    return False


def validate_email(email):
    if not User.objects.filter(email=email).exists():
        if re.match("^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\."
                    "[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:"
                    "[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)"
                    "+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$", email):
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


def _user_in_group(user, groupid):
    return GroupMember.objects.filter(group__id=groupid, user=user).exists()


def check_groupid(user, groupid):
    if groupid is None:
        return -2
    elif Group.objects.filter(id=groupid).exists() and _user_in_group(user, groupid):
        return groupid
    else:
        return 0


def validate_profile(first_name, last_name, birth, gender, country, city, institution):
    if re.match("^[A-Za-z]{0,30}$", first_name) and re.match("^[A-Za-z]{0,30}$", last_name):
        if gender == 0 or gender == 1:
            if re.match("^(?:(?!0000)[0-9]{4}/(?:(?:0[1-9]|1[0-2])/(?:0[1-9]|1[0-9]|2[0-8])|"
                        "(?:0[13-9]|1[0-2])/(?:29|30)|(?:0[13578]|1[02])-31)|(?:[0-9]{2}(?:0[48]|"
                        "[2468][048]|[13579][26])|(?:0[48]|[2468][048]|[13579][26])00)/02/29)$", birth):
                if re.match("^[A-Za-z0-9\s.!@#&\\\/\|:{}()';\"]{0,100}$", institution):
                    country, city = country.replace('-', ' '), city.replace('-', ' ')
                    if country in CITIES_TABLE and city in CITIES_TABLE[country]:
                        return True
    return False


def check_credits(user, bonus=''):
    if bonus == 'add':
        if user.extra.credits > 9999:
            return
    elif bonus == 'minus':
        if user.extra.credits < LINK_BONUS:
            return
    else:
        return
