# coding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('blog.views',
    url(r'^$', 'index', name='index'),
    url(r'^(?P<id>\d+)/$', 'homepage', name='home_of'),
)
