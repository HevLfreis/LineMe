#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/9
# Time: 13:51
import datetime

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models import Q

from Human.methods.avatar import create_avatar
from Human.methods.session import get_session_id
from Human.methods.utils import login_user, logger_join
from Human.methods.validation import validate_email, validate_username_exist
from Human.methods.validation import validate_passwd
from Human.models import Privacy, Extra, GroupMember, Link
from LineMe.settings import logger, DEBUG


def create_user(request, name, email, password, password2):

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

            if DEBUG:
                credit = 100
            else:
                credit = 30

            pri = Privacy(user=u)
            pri.save()
            extra = Extra(user=u,
                          gender=False,

                          # Todo: django timezone?
                          birth=datetime.date.today(),
                          credits=credit,
                          privacy=pri)

            extra.save()
            create_avatar(request, u.id, name)
        except Exception, e:
            logger.error(logger_join('Create', get_session_id(request), 'failed', e=e))
            logout(request)
            return -4

        logger.info(logger_join('Create', get_session_id(request)))
        return 0


########################################################################

def get_user_name(user):
    last = user.last_name
    first = user.first_name
    if len(first) is 0 and len(last) is 0:
        return user.username
    else:
        return first + ' ' + last


def get_user_groups(user):
    gms = GroupMember.objects.filter(user=user, is_joined=True)
    groups = [gm.group for gm in gms]
    return groups


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

        msgs += Link.objects.filter((Q(source_member=mm) & (Q(status=0) | Q(status=2) | Q(status=-2))) |
                                    Q(target_member=mm) & (Q(status=0) | Q(status=1) | Q(status=-1)),
                                    ~Q(creator=user))

    return msgs


def get_user_msgs_count(user):
    my_members = GroupMember.objects.filter(user=user)

    count = 0
    for mm in my_members:
        count += Link.objects.filter((Q(source_member=mm) & (Q(status=0) | Q(status=2) | Q(status=-2))) |
                                     Q(target_member=mm) & (Q(status=0) | Q(status=1) | Q(status=-1)),
                                     ~Q(creator=user)).count()
    return count


def get_user_invs(user, group_name=None):
    if group_name:
        invs = Link.objects.filter(creator=user, group__group_name__iexact=group_name).order_by('-created_time')
    else:
        invs = Link.objects.filter(creator=user).order_by('-created_time')
    return invs