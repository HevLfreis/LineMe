#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/11
# Time: 13:50


def create_session_id(request):
    if not (request.session.get('SessionID') and request.user.id):
        request.session['SessionID'] = '(' + request.META.get('REMOTE_ADDR') + ')' \
                                       + request.session.session_key + '[' + str(request.user.id) \
                                       + ',' + request.user.username + ']'


def get_session_id(request):
    sessionid = request.session.get('SessionID')
    if sessionid:
        return sessionid
    elif request.user:

        # Todo：cookie danger
        return '(' + request.META.get('REMOTE_ADDR') + ')' \
                    + request.COOKIES.get('sessionid') + '[' + str(request.user.id) \
                    + ',' + request.user.username + ']'
    else:
        return '(' + request.META.get('REMOTE_ADDR') + ')' \
                    + request.COOKIES.get('sessionid')


def get_session_consume(request, kw):
    val = request.session.get(kw)
    if val:
        del request.session[kw]
    return val
