# coding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('account.views',
    url(r'^$', 'index', name="index"),
    #url(r'^register/$', 'register', name="register"),
    url(r'^register/$', 'request_register', name='register'),
    url(r'^register/(?P<key>.+)/$', 'register', name='complete_register'),
    url(r'^login/$', 'login', name="login"),
    url(r'^logout/$', 'logout', name="logout"),
    url(r'^(?P<id>\d+)/$', 'user', name="show_user"),
)
