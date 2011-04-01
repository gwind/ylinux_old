# coding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('ydata.views',
    url(r'^uploadsf/(?P<id>\d+)/$', 'upload_single_file', name='uploadsf'),
    url(r'^attachment/(?P<id>\d+)/$', 'show_attachment', name='show_attachment'),
    url(r'^attachment/(?P<id>\d+)/remove/$', 'remove_attachment', name='delete_attachment'),
    url(r'^attachment/(?P<id>\d+)/download/$', 'download_attachment', name='download_attachment'),
)
