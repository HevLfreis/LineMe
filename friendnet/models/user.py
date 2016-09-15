#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/8/12
# Time: 15:25
from django.contrib.auth.models import User
from django.db import models

from friendnet.models.link import Link


class Privacy(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # Todo: more privacy settings, email privacy
    # link_me = models.BooleanField()
    # see_my_global = models.BooleanField()
    # link_need_my_confirm = models.BooleanField("Links need my confirmation", default=True)
    allow_group_recommendation = models.BooleanField("Group Recommendation", default=True)


class Extra(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    gender = models.BooleanField()
    birth = models.DateField()
    location = models.CharField(max_length=50, null=True)
    institution = models.CharField(max_length=150, null=True)
    privacy = models.ForeignKey(Privacy, on_delete=models.CASCADE)
    credits = models.IntegerField()


class Credit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    link = models.ForeignKey(Link, on_delete=models.CASCADE, null=True)
    action = models.IntegerField()
    timestamp = models.DateTimeField()



