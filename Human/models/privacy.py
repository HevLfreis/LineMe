#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/8/12
# Time: 15:26
from django.contrib.auth.models import User
from django.db import models


# all privacy need a default setting
class Privacy(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # Todo: more privacy settings, email privacy
    # link_me = models.BooleanField()
    # see_my_global = models.BooleanField()
    # link_need_my_confirm = models.BooleanField("Links need my confirmation", default=True)
    allow_group_recommendation = models.BooleanField("Group Recommendation", default=True)
