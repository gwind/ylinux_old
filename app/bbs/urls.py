# coding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('bbs.views',

    url(r'^$', 'index', name='index'),
    url(r'^(?P<id>\d+)/$', 'catalog_forum', name='subforum'),
)
