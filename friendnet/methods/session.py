#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/11
# Time: 13:50


def create_session_id(request):
    if not (request.session.get('SessionID') and request.user.id):
        request.session['SessionID'] = '(' + get_client_ip(request) + ')' \
                                       + request.session.session_key + '[' + str(request.user.id) \
                                       + ',' + request.user.username + ']'


def get_session_id(request):
    sessionid = request.session.get('SessionID')
    ip = get_client_ip(request)
    if sessionid:
        return sessionid
    elif request.user:

        # Todo：cookie danger
        return '(' + ip + ')' \
                    + request.COOKIES.get('sessionid') + '[' + str(request.user.id) \
                    + ',' + request.user.username + ']'
    else:
        return '(' + ip + ')' \
                    + request.COOKIES.get('sessionid')


def get_session_consume(request, kw):
    val = request.session.get(kw)
    if val is not None:
        del request.session[kw]
    return val


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
