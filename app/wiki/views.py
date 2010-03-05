# coding: utf-8

# Topic 表示一篇 Wiki 文章
# Post 表示一则回复

from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from ydata.models import Category,Catalog,Topic,Post
from ydata.forms import AddPostForm

from ydata.util import render_to,build_form


@render_to('wiki/index.html')
def index(request):
    """首页"""

    categorys = Category.objects.all()
    return {'categorys':categorys,}


# 指定 id ，显示对象的列表
@render_to('wiki/show_list.html')
def show_list (request, category_id, catalog_id, topic_id):
    """显示指定list"""

    # s 结尾表示符合条件的数据集合
    catalogs = None
    topics = None
    posts = None

    # 无 s 结尾表示一个对象
    category = None
    catalog = None
    topic = None

    # QuerySet 结果是一个列表
    # get 得到一个实例
    if category_id:
        category = Category.objects.get(pk=category_id)
        catalogs = Catalog.objects.filter(category=category_id)

    elif catalog_id:
        catalog = Catalog.objects.get(pk=catalog_id)
        topics = Topic.objects.filter(catalog=catalog_id)

    elif topic_id:
        topic = Topic.objects.get(pk=topic_id)
        posts = Post.objects.filter(topic=topic_id)


    # 两两一组的有效，其余为 None
    return {'category': category, 'catalogs': catalogs,
            'catalog': catalog, 'topics': topics,
            'topic': topic, 'posts': posts,
           }


# 显示 Post
def show_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    #count = post.topic.posts.filter(created__lt=post.created).count() + 1 
    #page = math.ceil(count / float(ydata_settings.TOPIC_PAGE_SIZE))
    #url = '%s?page=%d#post-%d' % (reverse('djangobb:topic', args=[post.topic.id]), page, post.id)
    url = reverse('wiki:show_topic', args=[post.topic.id])
    return HttpResponseRedirect(url)



# 创建 topic/post 
# 给了 catalog_id 就先创建 topic，否则给定 topic_id 直接创建 post
@render_to('wiki/add_post.html')
def add_post(request, catalog_id, topic_id):
    """添加一个Post（wiki 形式）"""
    catalog = None
    topic = None
    posts = None

    if catalog_id:
        # pk 应该是 primary key
        catalog = get_object_or_404(Catalog,pk=catalog_id)
        if not catalog.category.has_access(request.user):
            return HttpResponseForbidden()
    # 对， elif ，我们只需要 catalog_id 或 topic_id
    elif topic_id:
        topic = get_object_or_404(Topic,pk=topic_id)
        posts = topic.posts.all().select_related()
        if not topic.catalog.category.has_access(request.user):
            return HttpResponseForbidden()
    
    # 如果想回复 topic，但是 topic 已锁，则重定向到显示 topic
    if topic and topic.closed:
        return HttpResponseRedirect(topic.get_absolute_url())

    ip = request.META.get("REMOTE_ADDR", None)
    form = build_form(AddPostForm, request, topic=topic, catalog=catalog,
                      user=request.user, ip=ip,
                      initial={'markup': request.user.markup})
                      
    if form.is_valid():
        # AddPostForm 重定义 save 方法，创建 post 实例
        post = form.save()
        return HttpResponseRedirect(post.get_absolute_url())

    return {'form':form,
            'posts':posts,
            'topic':topic,
            'catalog':catalog,
           }

