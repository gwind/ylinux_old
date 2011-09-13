# coding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('me.views',
    url(r'^$', 'index', name='index'),
    url(r'^(?P<id>\d+)/$', 'home', name='home'),
    url(r'^(?P<id>\d+)/topics/$', 'topics', name='topics'),
    url(r'^(?P<id>\d+)/posts_by_other/$', 'posts_by_other', name='posts_by_other'),
    url(r'^(?P<id>\d+)/posts_for_other/$', 'posts_for_other', name='posts_for_other'),
)
