"""LineMe URL Configuration

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
from django.conf.urls import url

from Human import views

urlpatterns = [
    url(r'^$', views.redirect2main, name='redirect'),

    url(r'^login/$', views.lm_login, name='login'),
    url(r'^logout/$', views.lm_logout, name='logout'),
    url(r'^register/$', views.lm_register, name='register'),

    url(r'^home/$', views.home, name='home'),
    url(r'^msgpanel/(?P<page>[0-9]+)/$', views.msg_panel, name='homeMsg'),
    url(r'^msghandle/(?P<type>[0-1])/(?P<linkid>[0-9]+)/$', views.msg_handle, name='msgHandle'),

    url(r'^invpanel/(?P<page>[0-9]+)/$', views.inv_panel, name='homeInv'),
    url(r'^sendemail/(?P<page>[0-9]+)/$', views.send_email2unconfirmed, name='email'),

    #
    url(r'^ego/$', views.ego_network, name='ego'),
    url(r'^ego/(?P<groupid>[0-9]+)/$', views.ego_network, name='egoId'),

    url(r'^egraph/(?P<groupid>[0-9]+)/$', views.ego_graph, name='egraph'),
    url(r'^rcmdpanel/(?P<groupid>[0-9]+)/(?P<page>[0-9]+)/$', views.rcmd_panel, name='rcmd'),
    url(r'^updategraph/(?P<groupid>[0-9]+)/$', views.update_graph, name='updateGraph'),

    url(r'^global/$', views.global_network, name='global'),
    url(r'^global/(?P<groupid>[0-9]+)/$', views.global_network, name='globalId'),

    url(r'^ggraph/(?P<groupid>[0-9]+)/$', views.global_graph, name='ggraph'),

    #
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^settings/$', views.ego_network, name='settings'),

    #
    url(r'^group/(?P<groupid>[0-9]+)/$', views.manage_group, name='group'),
    url(r'^group/(?P<groupid>[0-9]+)/(?P<page>[0-9]+)/$', views.manage_group, name='groupPage'),
    url(r'^join/(?P<groupid>[0-9]+)$', views.join, name='join'),
    url(r'^upload/(?P<groupid>[0-9]+)/$', views.upload_members, name='uploadMembers'),
    #
    #
    url(r'^avatar/$', views.avatar, name='avatar'),
    url(r'^imghandle/$', views.img_handle, name='imgHandle'),
    #
    # url(r'^admin/', include(admin.site.urls)),
]
