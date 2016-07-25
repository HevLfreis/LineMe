#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/9
# Time: 13:51
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import re
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.db.models import Q

from Human.methods.session import create_session_id, get_session_id
from Human.methods.validation import validate_username, validate_passwd
from Human.models import GroupMember, Group
from LineMe.settings import logger


def login_user(request, username, password):

    if validate_username(username) and validate_passwd(password, password):
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                create_session_id(request)
                return True
    else:
        return False


def smart_search(request, kw, groupid, limit):

    logger.info(logger_join('Search', get_session_id(request), kw=kw))

    res = []

    if kw == '':
        return res

    if groupid:
        gms = GroupMember.objects.filter(Q(member_name__istartswith=kw) |
                                         Q(member_name__icontains=kw),
                                         group__id=groupid).order_by('member_name')[0:limit]
        for gm in gms:
            if gm.is_joined:
                res.append({"mid": gm.id, "uid": gm.user.id, "mname": gm.member_name})
            else:
                res.append({"mid": gm.id, "uid": 0, "mname": gm.member_name})

    else:
        gs = Group.objects.filter(group_name__istartswith=kw).order_by('group_name')[0:limit]
        for g in gs:
            res.append({"cid": g.creator.id, "gid": g.id, "name": g.group_name})

    return res


def input_filter(arg):
    if arg and (type(arg) is str or unicode):
        return re.sub(r"[^a-zA-Z0-9]", '', arg)
    else:
        return None


def send_email(receiver, subject, text):
    sender = 'hevlhayt@foxmail.com'
    subject = subject
    smtpserver = 'smtp.qq.com'
    username = 'hevlhayt'
    password = 'cypxypypmmvxbcii'

    msgRoot = MIMEMultipart('related')
    msgRoot['From'] = sender
    msgRoot['To'] = receiver
    msgRoot['Subject'] = subject

    msgText = MIMEText(text, 'html', 'utf-8')
    msgRoot.attach(msgText)

    # fp = open('h:\\python\\1.jpg', 'rb')
    # msgImage = MIMEImage(fp.read())
    # fp.close()

    # msgImage.add_header('Content-ID', '<image1>')
    # msgRoot.attach(msgImage)

    smtp = smtplib.SMTP()
    smtp.connect(smtpserver)
    smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, msgRoot.as_string())
    smtp.quit()


def logger_join(*args, **kwargs):
    if not args:
        return ''
    else:
        str_arg = ' '.join([str(arg) for arg in args])
        if not kwargs:
            return str_arg
        else:
            return str_arg + ' ' + ' '.join([k.upper()+':'+str(v) for k, v in kwargs.items()])