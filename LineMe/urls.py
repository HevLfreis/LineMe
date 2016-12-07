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
from django.conf.urls import url, include
from django.conf.urls.static import static

from friendnet import views
from LineMe import settings

urlpatterns = [
    url(r'^$', views.redirect2main, name='redirect'),

    url(r'^search/$', views.search, name='search'),

    url(r'^exp/(?P<groupid>[0-9]+)/$', views.exp, name='exp'),
    url(r'^exp/data/(?P<groupid>[0-9]+)/$', views.exp_data, name='expData'),


    url(r'^404/$', views.view_404, name='404'),
    #
    # url(r'^admin/', include(admin.site.urls)),

    url(r'', include('iauth.urls')),
    url(r'', include('friendnet.urls')),
    url(r'', include('question.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
