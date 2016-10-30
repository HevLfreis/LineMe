#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/8/12
# Time: 15:32
from django.contrib.auth.models import User
from django.db import models


class Group(models.Model):
    group_name = models.CharField(max_length=50)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.IntegerField()
    identifier = models.IntegerField()
    created_time = models.DateTimeField()
    deprecated = models.BooleanField()

    def has_member(self, user):
        return GroupMember.objects.filter(group=self, user=user, is_joined=True).exists()


class GroupMember(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    member_name = models.CharField(max_length=50)
    token = models.CharField(max_length=50, null=True)
    is_creator = models.BooleanField()
    is_joined = models.BooleanField()
    created_time = models.DateTimeField()
    joined_time = models.DateTimeField(null=True)

    # def __repr__(self):
    #     return self.member_name.decode('utf-8')

    def __str__(self):
        return self.member_name.encode('utf-8')


class MemberRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    message = models.CharField(max_length=200, null=True)
    created_time = models.DateTimeField()
    is_valid = models.BooleanField()
