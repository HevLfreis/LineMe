#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/8/12
# Time: 10:52
from django.db.models import Q
from django.shortcuts import get_object_or_404

from Human.models import GroupMember
from Human.models import Link


def simple_recommender(user, groupid):
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


def friend_recommender(user, groupid):
    if groupid < 0:
        return None

    my_member = get_object_or_404(GroupMember, group__id=groupid, user=user)

    links = Link.objects.filter(group__id=groupid)

    # group members already in your ego graph
    gmin = set([])
    for l in links.filter(creator=user):
        if l.source_member not in gmin or l.target_member not in gmin:
            gmin.add(l.source_member)
            gmin.add(l.target_member)

    # group members already not in your ego graph
    gms = set(GroupMember.objects.filter(group__id=groupid).exclude(user=user)) - gmin

    ls = links.filter(
        (Q(source_member=my_member) | Q(target_member=my_member))
        , group__id=groupid).exclude(creator=user)

    friends = {}
    for l in ls:
        if l.source_member == my_member and l.source_member not in gmin:
            if l.target_member in friends:
                friends[l.target_member] += 1
            else:
                friends[l.target_member] = 1

        elif l.target_member == my_member and l.target_member not in gmin:
            if l.source_member in friends:
                friends[l.source_member] += 1
            else:
                friends[l.source_member] = 1

    # top k members linking to you
    gmt = [k for k, v in sorted(friends.items(), key=lambda x: x[1], reverse=True)]

    gms -= set(gmt)

    # gms convert to a list
    gms = gmt + list(gms)

    return gms
