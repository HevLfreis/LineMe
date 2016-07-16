#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/9
# Time: 13:52
import ast

from django.shortcuts import get_object_or_404
from django.utils import timezone

from Human.methods.session import get_session_id
from Human.methods.utils import logger_join
from Human.models import GroupMember
from Human.models import Link
from LineMe.constants import SOURCE_LINK_CONFIRM_STATUS_TRANSITION_TABLE, SOURCE_LINK_REJECT_STATUS_TRANSITION_TABLE, \
    TARGET_LINK_REJECT_STATUS_TRANSITION_TABLE
from LineMe.constants import TARGET_LINK_CONFIRM_STATUS_TRANSITION_TABLE
from LineMe.settings import logger


# Todo: logger and security
def link_confirm(request, user, linkid):

    link = get_object_or_404(Link, id=linkid)
    gm = get_object_or_404(GroupMember, user=user, group=link.group, is_joined=True)

    now = timezone.now()
    link.confirmed_time = now

    if link.source_member == gm:
        link.status = SOURCE_LINK_CONFIRM_STATUS_TRANSITION_TABLE[link.status]

    elif link.target_member == gm:
        link.status = TARGET_LINK_CONFIRM_STATUS_TRANSITION_TABLE[link.status]

    else:
        logger.info(logger_join('Confirm', get_session_id(request), 'failed', lid=linkid))
        return -1

    link.save()
    logger.info(logger_join('Confirm', get_session_id(request), lid=linkid))
    return 0


def link_reject(request, user, linkid):

    link = get_object_or_404(Link, id=linkid)
    gm = get_object_or_404(GroupMember, user=user, group=link.group, is_joined=True)

    now = timezone.now()
    link.confirmed_time = now

    if link.source_member == gm:
        link.status = SOURCE_LINK_REJECT_STATUS_TRANSITION_TABLE[link.status]

    elif link.target_member == gm:
        link.status = TARGET_LINK_REJECT_STATUS_TRANSITION_TABLE[link.status]

    else:
        logger.info(logger_join('Reject', get_session_id(request), 'failed', lid=linkid))
        return -1

    link.save()
    logger.info(logger_join('Reject', get_session_id(request), lid=linkid))
    return 0


def update_links(request, new_links, creator, groupid):

    if not GroupMember.objects.filter(user=creator, group__id=groupid, is_joined=True).exists():
        return -1
        
    now = timezone.now()

    old_links = Link.objects.filter(creator=creator, group__id=groupid)
    links_index = {}

    for link in old_links:
        links_index[str(link.source_member.id) + ',' + str(link.target_member.id)] = link

    for link in ast.literal_eval(new_links):
        if link["source"] + ',' + link["target"] in links_index:
            links_index[link["source"] + ',' + link["target"]] = 0
        elif link["target"] + ',' + link["source"] in links_index:
            links_index[link["target"] + ',' + link["source"]] = 0
        else:
            links_index[link["source"] + ',' + link["target"]] = 1

    my_member = GroupMember.objects.get(group__id=groupid, user=creator)

    for k, v in links_index.items():
        if v is 0:
            continue
        elif v is 1:
            try:
                source = int(k.split(',')[0])
                target = int(k.split(',')[1])

                if source == my_member.id:
                    if not GroupMember.objects.filter(id=target, group__id=groupid).exists():
                        continue
                    else:
                        status = 1
                elif target == my_member.id:
                    if not GroupMember.objects.filter(id=source, group__id=groupid).exists():
                        continue
                    else:
                        status = 2
                else:

                    # Todo: maybe wrong ?
                    if not (GroupMember.objects.filter(id=source, group__id=groupid).exists() or
                            GroupMember.objects.filter(id=target, group__id=groupid).exists()):
                        continue
                    else:
                        status = 0

                l = Link(creator=creator,
                         source_member_id=source,
                         target_member_id=target,
                         group_id=groupid,
                         status=status,
                         created_time=now)
                l.save()

            except Exception, e:
                logger.error(logger_join('Update', get_session_id(request), 'failed', e=e))
                return -1
        else:
            v.delete()

    logger.info(logger_join('Update', get_session_id(request), gid=groupid))
    return 0
