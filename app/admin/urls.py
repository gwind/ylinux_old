# coding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('admin.views',

    url(r'^$', 'index', name="index"),
    url(r'^login/$', 'login', name="login"),


    # Permission
    url(r'^permission/$', 'permission', name='permissions'),
    url(r'^permission/(?P<id>\d+)/$', 'show_permission', name='show_permission'),
    url(r'^permission/(?P<id>\d+)/edit$', 'edit_permission', name='edit_permission'),
    url(r'^permission/add/$', 'add_permission', name='add_permission'),
    url(r'^permission/(?P<id>\d+)/del$', 'del_permission', name='del_permission'),


    # Group
    url(r'^group/$', 'group', name='groups'),
    url(r'^group/(?P<id>\d+)/$', 'show_group', name='show_group'),
    url(r'^group/(?P<id>\d+)/edit$', 'edit_group', name='edit_group'),
    url(r'^group/add/$', 'add_group', name='add_group'),
    url(r'^group/(?P<id>\d+)/del$', 'del_group', name='del_group'),

    
    # User
    url(r'^user/$', 'user', name='users'),
    url(r'^user/(?P<id>\d+)/$', 'show_user', name='show_user'),
    url(r'^user/(?P<id>\d+)/edit/$', 'edit_user', name='edit_user'),
    url(r'^user/add/$', 'add_user', name='add_user'),
    # 最好不要 del user， 禁止用户即可
    url(r'^user/(?P<id>\d+)/del$', 'del_user', name='del_user'),

    url(r'^user/email2all/$', 'email_to_all', name='email2all'),


    # Catalog
    url(r'^catalog/$', 'catalog', name='catalogs'),
    url(r'^catalog/(?P<id>\d+)/$', 'show_catalog', name='show_catalog'),
    url(r'^catalog/(?P<id>\d+)/del/$', 'del_catalog', name='del_catalog'),
    url(r'^catalog/(?P<id>\d+)/edit/$', 'edit_catalog', name='edit_catalog'),
    url(r'^catalog/(?P<parent_id>\d+)/add/$', 'add_catalog', name='add_sub_catalog'),
    url(r'^catalog/add/$', 'add_catalog', {'parent_id':None}, name='add_top_catalog'),


    # 危险！
    url(r'^reboot/$', 'reboot'),
)
