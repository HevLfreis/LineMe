#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/4
# Time: 12:48

import json
import os

from settings import STATICFILES_DIRS


PROJECT_NAME = 'LineMe'
STATIC_FOLDER = STATICFILES_DIRS[0]
GROUP_MAXSIZE = 5000
GROUP_CREATED_CREDITS_COST = 100

# Todo: implement identifier
IDENTIFIER = {0: 'Special Code', 1: 'Email', 2: 'Institution'}
GROUP_TYPE = {0: 'Normal', 1: 'RealTime'}
GROUP_REALTIME_ACTIVE_TIME = 0
LINK_STATUS = {-3: 'Both Reject', -21: 'Target Reject Source Confirmed', -12: 'Source Reject Target Confirmed',
               -2: 'Target Reject', -1: 'Source Reject', 0: 'Both Unconfirmed',
               1: 'Source Confirmed', 2: 'Target Confirmed', 3: 'Both Confirmed'}

SOURCE_LINK_CONFIRM_STATUS_TRANSITION_TABLE = {-3: -21, -21: -21, -12: 3,
                                               -2: -21, -1: 1, 0: 1,
                                               1: 1, 2: 3, 3: 3}

TARGET_LINK_CONFIRM_STATUS_TRANSITION_TABLE = {-3: -12, -21: 3, -12: -12,
                                               -2: 2, -1: -12, 0: 2,
                                               1: 3, 2: 2, 3: 3}

SOURCE_LINK_REJECT_STATUS_TRANSITION_TABLE = {-3: -3, -21: -3, -12: -12,
                                              -2: -3, -1: -1, 0: -1,
                                              1: -1, 2: -12, 3: -12}

TARGET_LINK_REJECT_STATUS_TRANSITION_TABLE = {-3: -3, -21: -21, -12: -3,
                                              -2: -2, -1: -3, 0: -2,
                                              1: -21, 2: -2, 3: -21}


CITIES_TABLE = json.load(file(os.path.join(STATIC_FOLDER, 'data/cities2.json')))
