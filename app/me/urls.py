# coding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('me.views',
    url(r'^$', 'index', name='index'),
    url(r'^(?P<id>\d+)/$', 'home', name='home'),
    url(r'^(?P<id>\d+)/topics/$', 'topics', name='topics'),
    url(r'^(?P<id>\d+)/topics/page_(?P<page>\d+)/$', 'topics', name='topics_page'),
    url(r'^(?P<id>\d+)/posts_by_other/$', 'posts_by_other', name='posts_by_other'),
    url(r'^(?P<id>\d+)/posts_by_other/page_(?P<page>\d+)/$', 'posts_by_other', name='posts_by_other_page'),
    url(r'^(?P<id>\d+)/posts_for_other/$', 'posts_for_other', name='posts_for_other'),
    url(r'^(?P<id>\d+)/posts_for_other/page_(?P<page>\d+)/$', 'posts_for_other', name='posts_for_other_page'),

    url(r'^(?P<id>\d+)/posts/to/$', 'posts', {'obj': 'to'}, name='to_posts'),
    url(r'^(?P<id>\d+)/posts/to/page_(?P<page>\d+)/$', 'posts', {'obj': 'to'}, name='to_posts_page'),
    url(r'^(?P<id>\d+)/posts/from/$', 'posts', {'obj': 'from'}, name='from_posts'),
    url(r'^(?P<id>\d+)/posts/from/page_(?P<page>\d+)/$', 'posts', {'obj': 'from'}, name='from_posts_page'),
)
