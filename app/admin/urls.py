# coding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('admin.views',

    url(r'^$', 'index', name="index"),
    url(r'^login/$', 'login', name="login"),

    # Permission
    url(r'^permission/$', 'permission', {'id':None}, name='show_permissions'),
    url(r'^permission/(?P<id>\d+)/$', 'permission', name='edit_permission'),
    url(r'^permission/add/$', 'add_permission', name='add_permission'),

    # Group
    url(r'^group/$', 'group', {'id':None}, name='show_groups'),
    url(r'^group/(?P<id>\d+)/$', 'group', name='edit_group'),
    url(r'^group/add/$', 'add_group', name='add_group'),
    
    # User
    url(r'^user/$', 'user', {'id':None}, name='show_users'),
    url(r'^user/(?P<id>\d+)/$', 'user', name='edit_user'),
    url(r'^user/add/$', 'add_user', name='add_user'),

    # Category
    url(r'^category/$', 'category', {'id':None}, name='show_categorys'),
    url(r'^category/(?P<id>\d+)/$', 'category', name='edit_category'),
    url(r'^category/add/$', 'add_category', name='add_category'),

    # Catalog
    url(r'^catalog/$', 'catalog', {'id':None}, name='show_catalogs'),
    url(r'^catalog/(?P<id>\d+)/$', 'catalog', name='edit_catalog'),
    url(r'^catalog/add/$', 'add_catalog', name='add_catalog'),

    # 危险！
    url(r'^reboot/$', 'reboot'),
)
