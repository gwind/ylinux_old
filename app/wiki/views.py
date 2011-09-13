# coding: utf-8

import time, datetime
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
#from django.contrib.syndication.views import Feed
from syndication.views import Feed

from account.decorators import login_required, permission_required
from ydata.models import Catalog,Topic,Post,Attachment
from ydata.forms import AddPostForm, \
    AddTopicForm, EditTopicForm

from ydata.util import render_to, build_form, get_parents, ylinux_get_ip
import xml.etree.ElementTree as ET

from wiki.utils import render_post

import math

@render_to('wiki/index.html')
def index(request):
    """首页"""

# 列出所有顶级目录
    catalogs = Catalog.objects.filter(parent=None)

# 论坛热帖
    recentd = datetime.date.today() - datetime.timedelta(30)
    hot_topics = Topic.objects.filter(updated__gt=recentd).order_by('-view_count')[:6]
#新帖
    new_topics = Topic.objects.all().order_by('-updated')[:10]
    posts = Post.objects.all().order_by('-updated')[:10]
    lastUpdataTime = int(time.time())
    return {'catalogs':catalogs,
            'hot_topics':hot_topics,
            'new_topics':new_topics,
            'title': u'[知识库]',
            'posts':posts,
            'lastUpdataTime': lastUpdataTime}


# 一些 DoesNotExist 的页面这里处理
@render_to('wiki/DoesNotExist.html')
def doesnotexist(request, type, id):
    return {'type':type, 'id':id}


@render_to('wiki/catalog.html')
def catalog(request, id=None, curpage=0):
    PERPAGE = 20

    if id:
        try:
            catalog = Catalog.objects.get(pk=id)
        except Catalog.DoesNotExist:
            url = reverse ('wiki:catalog_not_exist', args=[id])
            return HttpResponseRedirect(url)
        parents = get_parents (Catalog, id)
    else:
        catalog = None
        parents = None

    subcatalogs = Catalog.objects.filter(parent=id)
    topics = Topic.objects.filter(catalog=id).exclude(hidden=1).exclude(recycled=1).order_by('-updated')[curpage:20]
    pages = [ i+1 for i in range(int(math.ceil(Topic.objects.filter(catalog=id).exclude(hidden=1).exclude(recycled=1).count()/float(PERPAGE))))]

    edit_topic_perm = request.user.has_perm ('ydata.edit_topic')

    return {'catalog':catalog,
            'parents':parents,
            'subcatalogs':subcatalogs,
            'topics':topics,
            'title': u'[知识库] 目录浏览',
            'edit_topic_perm':edit_topic_perm,
            'curpage': curpage+1,
            'pages': pages}

@render_to('wiki/topic.html')
def topic(request, id):

    try:
        topic = Topic.objects.get(pk=id)
    except Topic.DoesNotExist:
        url = reverse ('wiki:topic_not_exist', args=[id])
        return HttpResponseRedirect(url)

    parents = get_parents (Catalog, topic.catalog.id)
    edit_topic_perm = request.user.has_perm ('ydata.edit_topic')

    posts = Post.objects.filter(topic=id, parent=None).order_by('created')
    POST_HTML = ''
    for p in posts:
        POST_HTML += render_post(request.user, p)


    return {'parents':parents, 'topic':topic,
            'edit_topic_perm':edit_topic_perm,
            'title': u"[知识库]%s" % topic.name,
            'POST_HTML': POST_HTML,
            'posts': posts}

@render_to('wiki/ajax_topic.html')
def ajax_topic(request, id):
    try:
        topic = Topic.objects.get(pk=id)
    except Topic.DoesNotExist:
        url = reverse ('wiki:topic_not_exist', args=[id])
        return HttpResponseRedirect(url)

    parents = get_parents (Catalog, topic.catalog.id)
    edit_topic_perm = request.user.has_perm ('ydata.edit_topic')

    return {'parents':parents, 'topic':topic,
            'edit_topic_perm':edit_topic_perm}

@render_to('wiki/post.html')
def post(request, id):

    try:
        post = Post.objects.get(pk=id)
    except Post.DoesNotExist:
        url = reverse ('wiki:post_not_exist', args=[id])
        return HttpResponseRedirect(url)

    return {'post':post}


# 发表回复
@login_required
@render_to('wiki/add_post.html')
def add_post(request, id):
    """添加一个Post（wiki 形式）"""

    if not request.user.is_authenticated():
        return HttpResponseForbidden('<h1>您没有这个权限！请 <a href="/account/login">登录</a></h1>')

    topic = get_object_or_404(Topic,pk=id)
    if not topic.catalog.has_access(request.user):
        return HttpResponseForbidden('<h1>您没有权限回复此帖！</h1>')
    # 如果 topic 已锁，则重定向到显示 topic
    if topic and topic.closed:
        return HttpResponseRedirect(topic.get_absolute_url())

    ip = ylinux_get_ip(request)

    form = build_form(AddPostForm, request, topic=topic,
                      user=request.user, ip=ip)

    if form.is_valid():
        post = form.save()
        # set last post
        topic.last_post = Post.objects.filter(topic=topic).latest('updated')
        topic.save()
        url = reverse ('wiki:show_topic', args=[post.topic.id])
        return HttpResponseRedirect(url)

    posts = topic.posts.all().select_related()
    return {'form':form, 'posts':posts, 'topic':topic}


# 代码实现 Plux <yfwz100@gmail.com>
@login_required
@render_to('wiki/ajax_add_topic.html')
def ajax_add_topic(request, id):
    if not id:
        return {'errors':'没有指定 Catalog'}

    catalog = get_object_or_404(Catalog,pk=id)
    if not catalog.has_access(request.user):
        return HttpResponseForbidden(u'<h2>你没有权限在此组中发贴！</h2>')
    parents = get_parents (Catalog, id)
    ip = ylinux_get_ip(request)

    form = build_form (AddTopicForm, request, 
           catalog=catalog, user=request.user, user_ip=ip)

    return {'parents':parents, 'form':form, 'id': id}


@login_required
@render_to('wiki/add_topic.html')
def add_topic(request,id):
    ''' id 是 Catalog '''
    
    if not id:
        return {'errors':'没有指定 Catalog'}

    catalog = get_object_or_404(Catalog,pk=id)
    if not catalog.has_access(request.user):
        return HttpResponseForbidden(u'<h2>你没有权限在此组中发贴！</h2>')
    parents = get_parents (Catalog, id)
    ip = ylinux_get_ip(request)

    form = build_form (AddTopicForm, request, 
           catalog=catalog, user=request.user, user_ip=ip)

    if form.is_valid():
        topic = form.save()
        # set last topic
        catalog.last_topic = topic
        catalog.save()
        url = reverse('wiki:show_topic', args=[topic.id])
        return HttpResponseRedirect(url)

    return {'parents':parents, 'form':form}


@login_required
@render_to('wiki/edit_topic.html')
def edit_topic(request, id):

    topic = get_object_or_404(Topic, pk=id)

    if topic.user != request.user:
        return HttpResponseForbidden('<h1>您没有这个权限！</h1>')

    parents = get_parents (Catalog, topic.catalog.id)
    ip = ylinux_get_ip(request)

    form = build_form (EditTopicForm, request,
                       text = topic.body,
                       user_ip = ip,
                       instance=topic)

    if form.is_valid():
        topic = form.save()
        url = reverse ('wiki:show_topic', args=[id])
        return HttpResponseRedirect(url)

    attachments = Attachment.objects.filter(topic=topic)
    return {'form':form,'parents':parents,'topic':topic, 'attachments':attachments}


@login_required
def manage_topic (request, id, type=None):

    topic = get_object_or_404 (Topic, pk=id)

    if topic.user != request.user:
        return HttpResponseForbidden('<h1>您没有这个权限！</h1>')

    c_id = topic.catalog.id

    if type is "delete":
        for p in topic.posts.all():
            p.delete()
        topic.delete()

    elif type is "recycled":
        topic.recycled = 1

    elif type is "hidden":
        topic.hidden = 1

    elif type is "disable_hidden":
        topic.hidden = 0

    elif type is "disable_recycled":
        topic.recycled = 0

    if type is not "delete":
        topic.save()

    url = reverse ('wiki:show_catalog', args=[c_id])
    return HttpResponseRedirect(url)


@login_required
def del_post (request, id):

    post = get_object_or_404 (Post, pk=id)
    t_id = post.topic.id

    if post.user != request.user:
        return HttpResponseForbidden('<h1>您没有这个权限！</h1>')

    post.delete()

    url = reverse ('wiki:show_topic', args=[t_id])
    return HttpResponseRedirect(url)


# django.utils.feedgenerator 是 low-level 调用，以后换成这个
class LatestTopicFeed(Feed):
    title = "YLinux.org 最新主题"
    link = "/topic/news/"
    description = "YLinux.org 站点的最近主题动态"

    def items(self):
        return Topic.objects.order_by('-updated')[:20]

    def item_title(self, item):
        return item.name

    def item_pubdate(self, item):
        return item.updated

    def item_description(self, item):
        return item.feed_desc


class LatestPostFeed(Feed):
    title = "YLinux.org 最新回复"
    link = "/post/news/"
    description = "YLinux.org 站点的最近回复动态"

    def items(self):
        return Post.objects.order_by('-updated')[:20]

    def item_title(self, item):
        return item.topic.name

    def item_pubdate(self, item):
        return item.updated

    def item_description(self, item):
        return item.body_html


# AJAX Call
@render_to('wiki/ajax_query_update.html')
def ajax_query_update(request, time):

    lastUpdataTime = datetime.datetime.fromtimestamp(float(time))
    topics = Topic.objects.filter(updated__gt = lastUpdataTime)
    posts = Post.objects.filter(updated__gt = lastUpdataTime)
    return {'topics':topics,
            'posts':posts}


@render_to('wiki/ajax_show_update.html')
def ajax_show_update(request):

    catalogs = Catalog.objects.filter(parent=None)
    topics = Topic.objects.all().order_by('-updated')[:10]
    posts = Post.objects.all().order_by('-updated')[:10]
    return {'catalogs':catalogs,
            'topics':topics,
            'title': u'[知识库]',
            'posts':posts}


@render_to('wiki/ajax_show_catalog.html')
def ajax_show_catalog(request, id):

    try:
        catalog = Catalog.objects.get(pk=id)
    except Catalog.DoesNotExist:
        #url = reverse ('wiki:catalog_not_exist', args=[id])
        #return HttpResponseRedirect(url)
        return { 'error': u'此目录不存在： %s' % id }

    parents = get_parents (Catalog, id)
    topics = Topic.objects.filter(catalog=id).exclude(hidden=1).exclude(recycled=1).order_by('-updated')[:5]

    edit_topic_perm = request.user.has_perm ('ydata.edit_topic')

    return {'catalog':catalog,
            'parents': parents,
            'topics':topics,
            'title': u'[知识库] 目录浏览',
            'edit_topic_perm':edit_topic_perm}


def ajax_show_posts(request, topicID=None, postID=None):

    if topicID:
        posts = Post.objects.filter(topic=topicID, parent=None).order_by('created')
        #posts = Post.objects.filter(topic=topicID).order_by('created')
    elif postID:
        posts = [get_object_or_404(Post,pk=postID),]
    else:
        return HttpResponse(u'显示 posts 出错')

    HTML = ''
#    HTML = '''
#<script type="text/javascript">
#  $(document).ready(function () {
#    $(".post-item").draggable();
#  })
#</script>
#'''
    for p in posts:
        HTML += render_post(request.user, p)
    return HttpResponse(HTML)


# 回复分为：
# 1. 回复 Topic
# 2. 回复 Post
@login_required
@render_to('wiki/replayAJAX.html')
def replayAJAX(request, topicID = None, postID = None):
    """ 通过 AJAX 方式回复 """

    replayID = None # 需要回复的 id
    parent_post = None

    if topicID:
        topic = get_object_or_404(Topic, pk = topicID)
        replayID = topicID
    elif postID:
        parent_post = get_object_or_404(Post, pk = postID)
        topic = get_object_or_404(Topic, pk = parent_post.topic.id)
        replayID = postID
    else:
        return HttpResponse(u'topicID 和 postID 必需要指定一个！')

    if request.method == 'GET':
        m = 'POST' if postID else 'TOPIC'
        ajaxFunc = 'ajax_replay(this, "%s", "%s")' % (m, replayID)
        return { 'method': 'GET',
                 'ajaxFunc' : ajaxFunc }

    else:

        if not request.user.is_authenticated():
            return HttpResponse(u'<h1>您没有权限！请 <a href="/account/login">登录</a></h1>')

        if not topic.catalog.has_access(request.user):
            return HttpResponse(u'<h1>您没有权限回复此帖！</h1>')

        # 如果 topic 已锁，则重定向到显示 topic
        if topic and topic.closed:
            return HttpResponse(u'主题已锁定，不可回复！')

        ip = ylinux_get_ip(request)

        post_body = request.POST.get("body", None)
        if len(post_body) < 2:
            return {'error': u'您的回复太短，至少2个字符！'}
        post = Post(topic = topic, user = request.user, user_ip = ip, markup = 'none', body = post_body, parent = parent_post)
        post.save()
        topic.post_count += 1
        topic.last_post = post
        topic.save()
        topic.catalog.post_count += 1
        topic.catalog.last_post = post
        topic.catalog.save()

        return {'method': 'POST', 'topic': topic, 'post': post}


@login_required
@render_to('wiki/editPostAJAX.html')
def editPostAJAX(request, postID):

    post = get_object_or_404(Post, pk = postID)

    if request.method == 'GET':
        return {'method': 'GET', 'post': post}

    post_body = request.POST.get('body', None)
    if not post_body:
        return HttpResponse(u'error: No contents found!')
    post.body = post_body
    post.save()

    post.topic.last_post = post
    post.topic.save()
    post.topic.catalog.last_post = post
    post.topic.catalog.save()

    return {'method': 'POST', 'post': post}
