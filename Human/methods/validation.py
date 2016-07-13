#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/11
# Time: 13:45
import re

from django.contrib.auth.models import User
from Human.models import Group, GroupMember

from LineMe.constants import CITIES_TABLE


def validate_username(name):
    if re.match("^[a-zA-Z][a-zA-Z0-9]{5,20}$", name):
        if not User.objects.filter(username=name).exists():
            return True
    return False


def validate_email(email):
    if User.objects.filter(email=email).exists():
        return False

    # Todo: email len > 7 ?
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email):
            return True
    return False


def validate_passwd(password, password2):
    if len(password) < 6 or password != password2:
        return False
    return True


def user_in_group(user, groupid):
    return GroupMember.objects.filter(group__id=groupid, user=user).exists()


def validate_groupname(name):
    if re.match("^[a-zA-Z][a-zA-Z0-9]{2,20}$", name):
        if not Group.objects.filter(group_name=name).exists():
            return True
    return False


def check_groupid(user, groupid):
    if groupid is None:
        return -2
    elif Group.objects.filter(id=groupid).exists() and user_in_group(user, groupid):
        return groupid
    else:
        return 0


# Todo: change to validate
# Todo: allow blank
def check_profile(first_name, last_name, birth, sex, country, city, institution):
    if re.match("^[A-Za-z]+$", first_name) and re.match("^[A-Za-z]+$", last_name):
        if sex == 0 or sex == 1:
            if re.match("^(?:(?!0000)[0-9]{4}/(?:(?:0[1-9]|1[0-2])/(?:0[1-9]|1[0-9]|2[0-8])|"
                        "(?:0[13-9]|1[0-2])/(?:29|30)|(?:0[13578]|1[02])-31)|(?:[0-9]{2}(?:0[48]|"
                        "[2468][048]|[13579][26])|(?:0[48]|[2468][048]|[13579][26])00)/02/29)$", birth):
                if re.match("^[A-Za-z\s]+$", institution):
                    if country in CITIES_TABLE and city in CITIES_TABLE[country]:
                        return True
    return False
