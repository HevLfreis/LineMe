#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/11
# Time: 13:38
import datetime

from Human.methods.session import get_session_id
from Human.methods.utils import logger_join
from Human.models import Extra
from LineMe.settings import logger


def update_profile(request, user, first_name, last_name, birth, gender, country, city, institution):
    try:
        user.first_name = first_name
        user.last_name = last_name

        ue = Extra.objects.get(user=user)
        ue.gender = gender
        ue.birth = datetime.datetime.strptime(birth, '%Y/%m/%d').date()
        ue.location = country + '-' + city
        ue.institution = institution
        user.save()
        ue.save()

    except Exception, e:
        # print 'Profile update failed: ', e
        logger.error(logger_join('Update', get_session_id(request), 'failed', e=e))
        return -1
    logger.info(logger_join('Update', get_session_id(request)))
    return 0
