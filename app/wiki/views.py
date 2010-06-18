# coding: utf-8

# Topic 表示一篇 Wiki 文章
# Post 表示一则回复

from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from ydata.models import Catalog,Topic,Post
from ydata.forms import AddPostForm, AddTopicForm

from ydata.util import render_to, build_form, get_parents


@render_to('wiki/index.html')
def index(request):
    """首页"""

    #catalogs = Catalog.objects.all()
    # 列出所有顶级目录
    catalogs = Catalog.objects.filter(parent=None)
    return {'catalogs':catalogs,}


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
    topics = Topic.objects.filter(catalog=id)

    return {'catalog':catalog,
            'parents':parents,
            'subcatalogs':subcatalogs,
            'topics':topics}


@render_to('wiki/topic.html')
def topic(request, id):

    try:
        topic = Topic.objects.get(pk=id)
    except Topic.DoesNotExist:
        url = reverse ('wiki:topic_not_exist', args=[id])
        return HttpResponseRedirect(url)

    parents = get_parents (Catalog, topic.catalog.id)
    #posts = topic.posts.all()
    posts = Post.objects.filter(topic=id).order_by('-updated')
    length = len(posts)
    posts = [(length-i, posts[i]) for i in xrange(length)]

    return {'parents':parents, 'topic':topic, 
            'posts':posts, 'total':length}


@render_to('wiki/post.html')
def post(request, id):

    try:
        post = Post.objects.get(pk=id)
    except Post.DoesNotExist:
        url = reverse ('wiki:post_not_exist', args=[id])
        return HttpResponseRedirect(url)

    return {'post':post}



# 创建 topic/post 
# 给了 catalog_id 就先创建 topic，否则给定 topic_id 直接创建 post
@render_to('wiki/add_post.html')
def add_post(request, catalog_id, topic_id):
    """添加一个Post（wiki 形式）"""
    catalog = None
    topic = None
    posts = None

    if catalog_id:
        catalog = get_object_or_404(Catalog,pk=catalog_id)
        if not catalog.has_access(request.user):
            return HttpResponseForbidden()
    # 对， elif ，我们只需要 catalog_id 或 topic_id
    elif topic_id:
        topic = get_object_or_404(Topic,pk=topic_id)
        posts = topic.posts.all().select_related()
        if not topic.catalog.has_access(request.user):
            return HttpResponseForbidden()
    
    # 如果想回复 topic，但是 topic 已锁，则重定向到显示 topic
    if topic and topic.closed:
        return HttpResponseRedirect(topic.get_absolute_url())

    #ip = request.META.get("REMOTE_ADDR", None)
    try:
        real_ip = request.META['HTTP_X_FORWARDED_FOR']
    except KeyError:
        ip = request.META.get('REMOTE_ADDR', None)
    else:
        ip = real_ip.split(",")[0].strip()

    form = build_form(AddPostForm, request, topic=topic, catalog=catalog,
                      user=request.user, ip=ip,
                      initial={'markup': request.user.markup})

    if form.is_valid():
        # AddPostForm 重定义 save 方法，创建 post 实例
        post = form.save()
        #return HttpResponseRedirect(topic.get_absolute_url())
        url = reverse ('wiki:show_topic', args=[post.topic.id])
        return HttpResponseRedirect(url)


    return {'form':form,
            'posts':posts,
            'topic':topic,
            'catalog':catalog}


@render_to('wiki/add_topic.html')
def add_topic(request,id):
    ''' id 是 Catalog '''
    
    if not id:
        return {'errors':'没有指定 Catalog'}

    catalog = get_object_or_404(Catalog,pk=id)
    if not catalog.has_access(request.user):
        return HttpResponseForbidden()
    parents = get_parents (Catalog, id)

    #ip = request.META.get('REMOTE_ADDR', None)
    try:
        real_ip = request.META['HTTP_X_FORWARDED_FOR']
    except KeyError:
        ip = request.META.get('REMOTE_ADDR', None)
    else:
        ip = real_ip.split(",")[0].strip()

    form = build_form (AddTopicForm, request, 
           catalog=catalog, user=request.user, user_ip=ip)

    if form.is_valid():
        topic = form.save()
        url = reverse('wiki:show_topic', args=[topic.id])
        return HttpResponseRedirect(url)

    return {'parents':parents, 'form':form}
