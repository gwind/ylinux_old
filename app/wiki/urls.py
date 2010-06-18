# coding: utf-8

from django.conf.urls.defaults import *

# patterns 的第一个元素是其他view的base路径
urlpatterns = patterns('wiki.views',

    url(r'^$', 'index', name='index'),

    # 一些不存在的对象
    url(r'^catalog_not_exist/(?P<id>\d+)/$', 'doesnotexist', {'type':'Catalog'}, name='catalog_not_exist'),
    url(r'^topic_not_exist/(?P<id>\d+)/$', 'doesnotexist', {'type':'Topic'}, name='topic_not_exist'),
    url(r'^post_not_exist/(?P<id>\d+)/$', 'doesnotexist', {'type':'Post'}, name='post_not_exist'),

    # Show Catalog : /前缀/catalog/<catalog-id>/
    # Show Topic : /前缀/topic/<topic-id>/
    # Show Post : /前缀/post/<post-id>/
    url(r'^catalog/(?P<id>\d+)/$', 'catalog', name='show_catalog'),
    url(r'^topic/(?P<id>\d+)/$', 'topic', name='show_topic'),
    url(r'^post/(?P<id>\d+)/$', 'post', name='show_post'),

    url(r'^catalog/(?P<id>\d+)/addtopic/$', 'add_topic', name='add_topic'),
    # Add Topic : /前缀/catalog/<catalog-id>/addtopic
    # Add Post : /前缀/topic/<topic-id>/addpost
    #url(r'^catalog/(?P<catalog_id>\d+)/topic/add/$', 'add_post', {'topic_id':None,}, name='add_topic'), 
    url(r'^topic/(?P<topic_id>\d+)/post/add/$', 'add_post', {'catalog_id':None,}, name='add_post'),

)
