# coding: utf-8

from django.conf.urls.defaults import *
from home.views import index,about,contact,coding,sitemap,robots

urlpatterns = patterns('',
    url(r'^$', index, name="index"),
    url(r'^about/$', about, name="about"),
    url(r'^contact/$', contact, name="contact"),
    url(r'^coding/$', coding),
    url(r'^sitemap.txt/$', sitemap),
    url(r'^robots.txt/$', robots),
)
