#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/4/24 
# Time: 11:11
#
from LineMe.settings import STATICFILES_DIRS

PROJECT_NAME = 'LineMe'
STATIC_FOLDER = STATICFILES_DIRS[0]
GROUP_MAXSIZE = 5000
GROUP_CREATED_CREDITS_COST = 10
IDENTIFIER = {0: 'Special Code', 1: 'Email', 2: 'Institution'}
GROUP_TYPE = {0: 'Normal', 1: 'RealTime'}
GROUP_REALTIME_ACTIVE_TIME = 0
Link_STATUS = {0: 'Both Reject', 1: 'Source Confirmed', 2: 'Target Confirmed', 3: 'Both Confirmed'}
