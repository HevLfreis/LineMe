#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/8/12
# Time: 15:25
from django.contrib.auth.models import User
from django.db import models

from Human.models.privacy import Privacy


class Extra(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    gender = models.BooleanField()
    birth = models.DateField()
    location = models.CharField(max_length=50, null=True)
    institution = models.CharField(max_length=150, null=True)
    privacy = models.ForeignKey(Privacy, on_delete=models.CASCADE)
    credits = models.IntegerField()
