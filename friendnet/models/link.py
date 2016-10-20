#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/8/12
# Time: 15:33
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from friendnet.models.group import Group, GroupMember


class Link(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    # Todo: new cascade, need check
    source_member = models.ForeignKey(GroupMember, related_name='source_member', on_delete=models.CASCADE)
    target_member = models.ForeignKey(GroupMember, related_name='target_member', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    status = models.IntegerField()
    confirmed_time = models.DateTimeField(null=True)
    created_time = models.DateTimeField()

    # def __repr__(self):
    #     return self.source_member.user+' '+self.target_member.user+' '+self.creator

    @staticmethod
    def check_redundancy(creator, groupid):

        links = Link.objects.filter(
            creator=creator,
            group__id=groupid
        )

        delete_list = set([])
        for link in links:
            if link.id in delete_list:
                continue
            red = links.filter((Q(source_member=link.source_member, target_member=link.target_member) |
                                Q(source_member=link.target_member, target_member=link.source_member)),
                               creator=link.creator).exclude(id=link.id)
            if red.exists():
                delete_list |= set([r.id for r in red])

        # print len(delete_list), delete_list

        for link_id in delete_list:
            links.get(id=link_id).delete()

        return links
