# coding: utf-8

from django.conf.urls.defaults import *
from wiki.views import LatestTopicFeed, LatestPostFeed

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

    # Add Topic :  /前缀/catalog/<catalog-id>/addtopic
    # Add Post  :  /前缀/topic/<topic-id>/addpost
    url(r'^topic/(?P<id>\d+)/addpost/$', 'add_post', name='add_post'),
    url(r'^catalog/(?P<id>\d+)/addtopic/$', 'add_topic', name='add_topic'),

    # Edit Topic :  /前缀/topic/<topic-id>/edit/
    url(r'^topic/(?P<id>\d+)/edit/$', 'edit_topic', name='edit_topic'),

    # Delete Topic : /前缀/topic/<topic-id>/delete/
    url(r'^topic/(?P<id>\d+)/delete/$', 'manage_topic', {'type':'delete'}, name='del_topic'),
    url(r'^topic/(?P<id>\d+)/recycled/$', 'manage_topic', {'type':'recycled'}, name='recycled_topic'),
    url(r'^topic/(?P<id>\d+)/hidden/$', 'manage_topic', {'type':'hidden'}, name='hidden_topic'),
    url(r'^topic/(?P<id>\d+)/disable_recycled/$', 'manage_topic', {'type':'disable_recycled'}, name='disable_recycled_topic'),
    url(r'^topic/(?P<id>\d+)/disable_hidden/$', 'manage_topic', {'type':'disable_hidden'}, name='disable_hidden_topic'),

    url(r'^post/(?P<id>\d+)/delete/$', 'del_post', name='del_post'),

    # Feeds
    url(r'^topic/news/$', LatestTopicFeed(), name='topic_news'),
    url(r'^post/news/$', LatestPostFeed(), name='post_news'),

    # AJAX Call
    url(r'^query_update/(?P<time>\d+)/ajax/$', 'ajax_query_update', name='ajax_query_update'),
    url(r'^show_update/ajax/$', 'ajax_show_update', name='ajax_show_update'),
    url(r'^catalog/(?P<id>\d+)/ajax/$', 'ajax_show_catalog', name='ajax_show_catalog'),
    url(r'^topic/(?P<topicID>\d+)/ajax_show_posts/$', 'ajax_show_posts', name='ajax_show_topic_posts'),
    url(r'^post/(?P<postID>\d+)/ajax_show_posts/$', 'ajax_show_posts', name='ajax_show_post_posts'),
    url(r'^catalog/(?P<id>\d+)/addtopic/ajax/$', 'ajax_add_topic', name='ajax_add_topic'), # Plux <yfwz100@gmail.com>

    # 回复
    url(r'^topic/(?P<topicID>\d+)/replayAJAX/$', 'replayAJAX', name="replayTopicAJAX"),
    url(r'^post/(?P<postID>\d+)/replayAJAX/$', 'replayAJAX', name="replayPostAJAX"),
)
