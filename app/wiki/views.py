# coding: utf-8

from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
#from django.contrib.syndication.views import Feed
from syndication.views import Feed

from account.decorators import login_required, permission_required
from ydata.models import Catalog,Topic,Post,Attachment
from ydata.forms import AddPostForm, \
    AddTopicForm, EditTopicForm

from ydata.util import render_to, build_form, get_parents, ylinux_get_ip


@render_to('wiki/index.html')
def index(request):
    """首页"""

    catalogs = Catalog.objects.all()
    # 列出所有顶级目录
    #catalogs = Catalog.objects.filter(parent=None)
    topics = Topic.objects.all()
    posts = Post.objects.all()
    return {'catalogs':catalogs,
            'topics':topics,
            'posts':posts}


# 一些 DoesNotExist 的页面这里处理
@render_to('wiki/DoesNotExist.html')
def doesnotexist(request, type, id):
    return {'type':type, 'id':id}


@render_to('wiki/catalog.html')
def catalog(request, id):

    try:
        catalog = Catalog.objects.get(pk=id)
    except Catalog.DoesNotExist:
        url = reverse ('wiki:catalog_not_exist', args=[id])
        return HttpResponseRedirect(url)

    parents = get_parents (Catalog, id)
    subcatalogs = Catalog.objects.filter(parent=id)
    topics = Topic.objects.filter(catalog=id).exclude(hidden=1).exclude(recycled=1)

    edit_topic_perm = request.user.has_perm ('ydata.edit_topic')

    return {'catalog':catalog,
            'parents':parents,
            'subcatalogs':subcatalogs,
            'topics':topics,
            'edit_topic_perm':edit_topic_perm}


@render_to('wiki/topic.html')
def topic(request, id):

    try:
        topic = Topic.objects.get(pk=id)
    except Topic.DoesNotExist:
        url = reverse ('wiki:topic_not_exist', args=[id])
        return HttpResponseRedirect(url)

    parents = get_parents (Catalog, topic.catalog.id)
    posts = Post.objects.filter(topic=id).order_by('-updated')
    length = len(posts)
    posts = [(length-i, posts[i]) for i in xrange(length)]
    edit_topic_perm = request.user.has_perm ('ydata.edit_topic')

    return {'parents':parents, 'topic':topic, 
            'posts':posts, 'total':length,
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
