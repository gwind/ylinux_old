# coding: utf-8

from django.conf.urls.defaults import *
from account.views import register,login,logout

urlpatterns = patterns('',
    url(r'^register/$', register, name="register"),
    url(r'^login/$', login, name="login"),
    url(r'^logout/$', logout, name="logout"),
)
