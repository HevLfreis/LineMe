"""CNC2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from Human import views

urlpatterns = [
    url(r'^demo/$', views.home, name='demo'),

    url(r'^login/$', views.my_login, name='login'),
    url(r'^logout/$', views.my_logout, name='logout'),
    url(r'^register/$', views.my_register, name='register'),

    url(r'^home/$', views.home, name='home'),

    url(r'^ego/$', views.ego, name='ego'),
    url(r'^graph/(?P<groupid>[0-9]+)/$', views.graph, name='graph'),
    url(r'^sugmember/(?P<groupid>[0-9]+)/(?P<page>[0-9]+)/$', views.sugmember, name='sugmember'),
    url(r'^links/(?P<groupid>[0-9]+)/$', views.links, name='links'),

    url(r'^group/$', views.manage_group, name='group'),
    url(r'^join/$', views.join, name='join'),


    url(r'^avatar/$', views.avatar, name='avatar'),
    url(r'^imghandle/$', views.imghandle, name='imghandle'),

    url(r'^404/$', views.error_404, name='404'),

]
