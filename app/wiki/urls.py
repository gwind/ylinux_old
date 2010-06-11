# coding: utf-8

from django.conf.urls.defaults import *

# patterns 的第一个元素是其他view的base路径
urlpatterns = patterns('wiki.views',

    url(r'^$', 'index', name='index'),


    url(r'^catalog/(?P<catalog_id>\d+)/$','show_list',
        {'topic_id':None,}, name='show_catalog'), 


    # 显示目录： /wiki/id/
    url(r'^(?P<id>\d+)/$', 'catalog', name='catalog'),

    # Topic
    url(r'^topic/(?P<topic_id>\d+)/$', 'show_list',
        {'catalog_id':None,}, name='show_topic'), 

    url(r'^catalog/(?P<catalog_id>\d+)/topic/add/$', 'add_post', {'topic_id':None,}, name='add_topic'), 


    # Post
    url(r'^topic/(?P<topic_id>\d+)/post/add/$', 'add_post', {'catalog_id':None,}, name='add_post'),
    url('^post/(?P<post_id>\d+)/$', 'show_post', name='show_post'),
)
