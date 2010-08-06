# coding: utf-8

from django.conf.urls.defaults import *
from home.views import index,about,contact,coding

urlpatterns = patterns('',
    url(r'^$', index, name="index"),
    url(r'^about/$', about, name="about"),
    url(r'^contact/$', contact, name="contact"),
    url(r'^coding/$', coding),                       
)
