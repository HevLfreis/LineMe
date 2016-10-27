#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/8/12
# Time: 10:52
from django.db.models import Q

from friendnet.methods.basic.group import get_group_joined_num
from friendnet.methods.basic.groupmember import myself_member
from friendnet.methods.basic.user import get_user_name
from friendnet.models import GroupMember, Group
from friendnet.models import Link


class Recommender:
    def __init__(self, user):
        self.user = user

    def simple(self, groupid):
        if groupid < 0:
            return None

        gmout, gmin = [], []
        ls = Link.objects.filter(
            group__id=groupid,
            creator=self.user
        )

        for l in ls:
            if l.source_member not in gmin or l.target_member not in gmin:
                gmin.append(l.source_member)
                gmin.append(l.target_member)

        for gm in GroupMember.objects.filter(
                group__id=groupid
        ).exclude(user=self.user).order_by('-is_joined'):

            if gm not in gmin:
                gmout.append(gm)

        return gmout

    def friend(self, groupid):
        if groupid < 0:
            return None

        my_member = myself_member(self.user, groupid)

        links = Link.objects.filter(group__id=groupid)

        # group members already in your ego graph
        gmin = set([])
        for l in links.filter(creator=self.user):
            if l.source_member not in gmin or l.target_member not in gmin:
                gmin.add(l.source_member)
                gmin.add(l.target_member)

        # group members already not in your ego graph
        gms = set(GroupMember.objects.filter(
            group__id=groupid
        ).exclude(user=self.user)) - gmin

        ls = links.filter(
            (Q(source_member=my_member) | Q(target_member=my_member)),
            group__id=groupid
        ).exclude(creator=self.user)

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

    def group(self):

        if not self.user.privacy.allow_group_recommendation:
            return []

        gms = GroupMember.objects.filter(
            member_name=get_user_name(self.user),
            is_joined=False
        )

        sug = set(gm.group for gm in gms if not gm.group.has_member(self.user))

        # Todo: only recommend 5 no validation public group, may add algo
        for no_val_group in Group.objects.filter(identifier=2, deprecated=False).exclude(creator=self.user)[0:5]:
            if not GroupMember.objects.filter(
                    group=no_val_group,
                    user=self.user
            ).exists():
                sug.add(no_val_group)

        res = {s: get_group_joined_num(s) for s in sug}

        return res
