# coding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('ylab.views',
    url(r'^time$', 'time', name='time'),
    url(r'^uploadsf$', 'upload_single_file', name='uploadsf'),
)
