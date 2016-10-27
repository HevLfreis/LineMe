#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/9
# Time: 13:52
import json

from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from LineMe.constants import SOURCE_LINK_CONFIRM_STATUS_TRANSITION_TABLE, SOURCE_LINK_REJECT_STATUS_TRANSITION_TABLE, \
    TARGET_LINK_REJECT_STATUS_TRANSITION_TABLE, TARGET_LINK_CONFIRM_STATUS_TRANSITION_TABLE
from LineMe.settings import logger
from LineMe.utils import logger_join
from friendnet.methods.basic.groupmember import myself_member
from friendnet.models import GroupMember
from friendnet.models import Link
from iauth.methods.session import get_session_id


def get_link(linkid):
    return get_object_or_404(Link, id=linkid)


def link_confirm(request, user, link):
    my_member = myself_member(user, link.group.id)

    now = timezone.now()
    link.confirmed_time = now
    old_status = link.status

    if link.source_member == my_member:
        link.status = SOURCE_LINK_CONFIRM_STATUS_TRANSITION_TABLE[old_status]

    elif link.target_member == my_member:
        link.status = TARGET_LINK_CONFIRM_STATUS_TRANSITION_TABLE[old_status]

    else:
        logger.info(logger_join('Confirm', get_session_id(request), 'failed', lid=link.id))
        return -1

    link.save()
    # credit_processor(link, old_status)

    logger.info(logger_join('Confirm', get_session_id(request), lid=link.id))
    return 0


def link_reject(request, user, link):
    my_member = myself_member(user, link.group.id)

    now = timezone.now()
    link.confirmed_time = now
    old_status = link.status

    if link.source_member == my_member:
        link.status = SOURCE_LINK_REJECT_STATUS_TRANSITION_TABLE[old_status]

    elif link.target_member == my_member:
        link.status = TARGET_LINK_REJECT_STATUS_TRANSITION_TABLE[old_status]

    else:
        logger.info(logger_join('Reject', get_session_id(request), 'failed', lid=link.id))
        return -1

    link.save()
    # credit_processor(link, old_status)

    logger.info(logger_join('Reject', get_session_id(request), lid=link.id))
    return 0


def link_aggregate(user, this_link):
    my_member = myself_member(user, this_link.group.id)

    if this_link.source_member == my_member:
        another_member = this_link.target_member
    else:
        another_member = this_link.source_member

    all_links = Link.objects.filter(
        (Q(source_member=my_member) & Q(target_member=another_member) &
         (Q(status=0) | Q(status=2) | Q(status=-2))) |
        (Q(target_member=my_member) & Q(source_member=another_member) &
         (Q(status=0) | Q(status=1) | Q(status=-1))),
        ~Q(creator=user), group=this_link.group
    )

    return all_links


def link_confirm_aggregate(request, user, link):
    all_links = link_aggregate(user, link)

    for l in all_links:
        status = link_confirm(request, user, l)
        if status != 0:
            return -1
    return 0


def link_reject_aggregate(request, user, link):
    all_links = link_aggregate(user, link)

    for l in all_links:
        status = link_reject(request, user, l)
        if status != 0:
            return -1
    return 0


@transaction.atomic
def update_links(request, new_links, creator, groupid):
    if not GroupMember.objects.filter(
            user=creator,
            group__id=groupid,
            is_joined=True
    ).exists():

        return -1

    def group_member_existed(*ids):
        for i in ids:
            if not GroupMember.objects.filter(
                            id=i,
                            group__id=groupid
                    ).exists():
                return False
        return True

    now = timezone.now()

    old_links = Link.check_redundancy(creator, groupid)

    links_index, save_list = {}, []

    for link in old_links:
        links_index[str(link.source_member.id) + ',' + str(link.target_member.id)] = link

    for link in json.loads(new_links):
        if link["source"] + ',' + link["target"] in links_index:
            links_index[link["source"] + ',' + link["target"]] = 0
        elif link["target"] + ',' + link["source"] in links_index:
            links_index[link["target"] + ',' + link["source"]] = 0
        else:
            links_index[link["source"] + ',' + link["target"]] = 1

    my_member = myself_member(creator, groupid)

    for k, v in links_index.items():
        try:
            if v == 0:
                continue
            elif v == 1:

                source = int(k.split(',')[0])
                target = int(k.split(',')[1])

                if source == my_member.id:
                    if not group_member_existed(target):
                        continue
                    else:
                        status = 1
                elif target == my_member.id:
                    if not group_member_existed(source):
                        continue
                    else:
                        status = 2
                else:

                    # Todo: maybe wrong ?
                    if not group_member_existed(source, target):
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

            else:
                v.delete()

        except Exception, e:
            logger.error(logger_join('Update', get_session_id(request), 'failed', e=e))
            return -1

    logger.info(logger_join('Update', get_session_id(request), gid=groupid))
    return 0

