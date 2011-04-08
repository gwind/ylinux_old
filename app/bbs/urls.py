# coding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('bbs.views',

    url(r'^$', 'index', name='index'),
    #url(r'^(?P<id>\d+)/$', 'catalog_forum', name='subforum'),
    url(r'^(?P<id>\d+)/$', 'catalog', name='catalog'),
    url(r'^topic/(?P<id>\d+)/$', 'topic', name='topic'),

    url(r'^forum_not_exist/(?P<id>\d+)/$', 'doesnotexist', {'type':'Forum'}, name='forum_not_exist'),
    url(r'^topic_not_exist/(?P<id>\d+)/$', 'doesnotexist', {'type':'Topic'}, name='topic_not_exist'),
    url(r'^post_not_exist/(?P<id>\d+)/$', 'doesnotexist', {'type':'Post'}, name='post_not_exist'),
)
