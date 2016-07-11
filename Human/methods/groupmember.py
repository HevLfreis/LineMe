#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/9
# Time: 13:50


# Todo: token multiple check, and fix same token
from django.db.models import Q
from django.utils import timezone

from Human.methods.sessionid import get_session_id
from Human.methods.user import get_user_name
from Human.methods.utils import logger_join
from Human.models import GroupMember, Link
from LineMe.settings import logger


def create_group_member(request, group, name, identifier, user=None):
    now = timezone.now()

    if GroupMember.objects.filter(member_name=name, group=group).exists():
        return -1

    try:
        m = GroupMember(group=group,
                        user=user,
                        member_name=name,
                        token=identifier,
                        is_creator=False,
                        is_joined=False,
                        created_time=now)
        m.save()
    except Exception, e:
        # print 'Group member create: ', e
        logger.error(logger_join('Create', get_session_id(request), 'failed', e=e))
        return None
    logger.info(logger_join('Create', get_session_id(request), mid=m.id))
    return m


def member_join(request, user, group, identifier):
    now = timezone.now()
    try:
        m = GroupMember.objects.get((Q(member_name=get_user_name(user)) | Q(member_name=user.username)),
                                    group=group, token=identifier)
        m.is_joined = True
        m.user = user
        m.joined_time = now
        m.save()
    except Exception, e:
        logger.error(logger_join('Join', get_session_id(request), 'failed', e=e))
        return -1

    logger.info(logger_join('Join', get_session_id(request), mid=m.id))
    return 0


def member_recommender(user, groupid):
    if groupid < 0:
        return None
    gmout = []
    gmin = []
    ls = Link.objects.filter(group__id=groupid, creator=user)

    for l in ls:
        if l.source_member not in gmin or l.target_member not in gmin:
            gmin.append(l.source_member)
            gmin.append(l.target_member)

    for gm in GroupMember.objects.filter(group__id=groupid).exclude(user=user).order_by('-is_joined'):
        if gm not in gmin:
            gmout.append(gm)

    return gmout