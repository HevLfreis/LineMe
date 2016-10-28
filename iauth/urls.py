#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/10/26
# Time: 17:36
from django.conf.urls import url

from iauth import views

urlpatterns = [

    #
    url(r'^login/$', views.i_login, name='login'),
    url(r'^logout/$', views.i_logout, name='logout'),
    url(r'^register/$', views.i_register, name='register'),

    #
    url(r'^password/$', views.reset, name='password'),
    url(r'^forget/$', views.forget, name='forget'),
    url(r'^resetbyemail/(?P<token>[0-9a-zA-Z]+)/$', views.reset_by_email, name='resetByEmail'),
]