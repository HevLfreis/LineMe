#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/5/16 
# Time: 19:33
# friendnet urls configuration
from django.conf.urls import url

from friendnet import views

urlpatterns = [

    #
    url(r'^home/$', views.home, name='home'),
    url(r'^msgpanel/$', views.msg_panel, name='homeMsg'),
    url(r'^msghandle/$', views.msg_handle, name='msgPost'),
    url(r'^msghandle/(?P<mtype>[0-3])/(?P<handleid>[0-9]+)/$', views.msg_handle, name='msgHandle'),

    url(r'^invpanel/$', views.inv_panel, name='homeInv'),
    url(r'^sendemail/(?P<page>[0-9]+)/$', views.send_email2unconfirmed, name='email'),

    #
    url(r'^ego/$', views.ego_network, name='ego'),
    url(r'^ego/(?P<groupid>[0-9]+)/$', views.ego_network, name='egoId'),

    url(r'^egraph/(?P<groupid>[0-9]+)/$', views.ego_graph, name='eGraph'),
    url(r'^rcmdpanel/(?P<groupid>[0-9]+)/$', views.rcmd_panel, name='rcmd'),
    url(r'^upgraph/(?P<groupid>[0-9]+)/$', views.update_graph, name='updateGraph'),

    url(r'^global/$', views.global_network, name='global'),
    url(r'^global/(?P<groupid>[0-9]+)/$', views.global_network, name='globalId'),

    url(r'^ggraph/(?P<groupid>[0-9]+)/$', views.global_graph, name='gGraph'),
    url(r'^gmap/(?P<groupid>[0-9]+)/$', views.global_map, name='gMap'),
    url(r'^gthree/(?P<groupid>[0-9]+)/$', views.global_three, name='gThree'),

    #
    url(r'^profile/$', views.profile, name='profile'),

    #
    url(r'^group/(?P<groupid>[0-9]+)/$', views.manage_group, name='group'),
    url(r'^join/(?P<groupid>[0-9]+)/$', views.join, name='join'),
    url(r'^jreq/(?P<groupid>[0-9]+)/$', views.join_request, name='joinRequest'),
    url(r'^jcof/(?P<groupid>[0-9]+)/(?P<requestid>[0-9]+)/$', views.join_confirm, name='joinConfirm'),
    url(r'^jdec/(?P<groupid>[0-9]+)/(?P<requestid>[0-9]+)/$', views.join_decline, name='joinDecline'),
    url(r'^upload/(?P<groupid>[0-9]+)/$', views.upload_members, name='uploadMembers'),

    #
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^settings/$', views.settings, name='avatar'),
    url(r'^imghandle/$', views.img_handle, name='imgHandle'),
    url(r'^privacy/$', views.privacy_save, name='privacy'),
]
