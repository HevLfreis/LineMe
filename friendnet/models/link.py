#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/8/12
# Time: 15:33
from django.contrib.auth.models import User
from django.db import models

from friendnet.models.group import Group, GroupMember


class Link(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    source_member = models.ForeignKey(GroupMember, related_name='source_member')
    target_member = models.ForeignKey(GroupMember, related_name='target_member')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    status = models.IntegerField()
    confirmed_time = models.DateTimeField(null=True)
    created_time = models.DateTimeField()
