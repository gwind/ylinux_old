# coding: utf-8

from account.models import User
from ydata.models import Topic, Post
from ydata.util import render_to, build_form, get_parents



@render_to('me/index.html')
def index(request):

    users = User.objects.all().order_by('-last_login')[:20]
    posts = Post.objects.all().order_by('-updated')[:20]
    topics = Topic.objects.all().order_by('-updated')[:20]

    return {'title': u"这就是我！", 'users': users, 'topics': topics, 'posts': posts}


@render_to('me/home.html')
def home(request, id):
    ''' 指定 id 的用户 ME HOME '''

    try:
        owner = User.objects.get(pk=id)
    except User.DoesNotExist:
        url = reverse ('account:user_not_exist', args=[id])
        return HttpResponseRedirect(url)

    topic_count = len(Topic.objects.filter(user=id).order_by('-updated'))
    post_count = len(Post.objects.filter(user=id).order_by('-updated'))
    fpost_count = len(Post.objects.filter(touser=id).order_by('-updated'))

    return {'title': u'欢迎访问 %s 的首页' % owner.username, 
            'owner':owner, 'owner_id': id, 
            'topic_count': topic_count, 'post_count': post_count, 'fpost_count': fpost_count}


@render_to('me/topics.html')
def topics(request, id, page=1):
    ''' 分页显示用戶发表的主题 '''

    page = int(page) - 1
    error = ''
    total_page = 0

    try:
        owner = User.objects.get(pk=id)
    except User.DoesNotExist:
        url = reverse ('account:user_not_exist', args=[id])
        return HttpResponseRedirect(url)

    if page < 0:
        topics = []
        error = u'第 %s 页主题不存在!' % (page + 1)
    else:
        start = page * 10
        end = page * 10 + 10
        topics = Topic.objects.filter(user=id).order_by('-updated')
        total_page = len(topics) / 10 + 1
        if ( page * 10 ) > len(topics):
            error = u'第 %s 页主题不存在!' % (page + 1)
            topics = []
        else:
            topics = topics[start:end]

    page_list = range(1, total_page + 1) if total_page > 1 else []
    return {'title': u'%s 发表的文章' % owner.username, 
            'owner': owner, 'owner_id': id, 'topics': topics,
            'error': error, 'last_page': total_page, 'pre_page': page, 'next_page': page + 2,
            'page_list': page_list, 'cur_page': page + 1}


@render_to('me/posts_by_other.html')
def posts_by_other(request, id, page=1):
    ''' 分页显示关于用户的所有评论 '''

    page = int(page) - 1
    error = ''
    total_page = 0

    try:
        user = User.objects.get(pk=id)
    except User.DoesNotExist:
        url = reverse ('account:user_not_exist', args=[id])
        return HttpResponseRedirect(url)

    if page < 0:
        posts = []
        error = u'第 %s 页主题不存在!' % (page + 1)
    else:
        start = page * 10
        end = page * 10 + 10
        posts = Post.objects.filter(touser=id).order_by('-updated')
        total_page = len(posts) / 10 + 1
        if ( page * 10 ) > len(posts):
            error = u'第 %s 页评论不存在!' % (page + 1)
            posts = []
        else:
            posts = posts[start:end]

    return {'title': u'%s 得到的评论' % user.username, 
            'owner':user, 'owner_id': id, 'posts': posts,
            'error': error, 'last_page': total_page, 'pre_page': page, 'next_page': page + 2,
            'page_list': range(1, total_page + 1), 'cur_page': page + 1}



@render_to('me/posts_for_other.html')
def posts_for_other(request, id, page=1):
    ''' 分页显示用户发表的所有评论 '''

    page = int(page) - 1
    error = ''
    total_page = 0

    try:
        owner = User.objects.get(pk=id)
    except User.DoesNotExist:
        url = reverse ('account:user_not_exist', args=[id])
        return HttpResponseRedirect(url)

    if page < 0:
        posts = []
        error = u'第 %s 页主题不存在!' % (page + 1)
    else:
        start = page * 10
        end = page * 10 + 10
        posts = Post.objects.filter(user=id).order_by('-updated')
        total_page = len(posts) / 10 + 1
        if ( page * 10 ) > len(posts):
            error = u'第 %s 页评论不存在!' % (page + 1)
            posts = []
        else:
            posts = posts[start:end]

    return {'title': u'%s 得到的评论' % owner.username, 
            'owner':owner, 'owner_id': id, 'posts': posts,
            'error': error, 'last_page': total_page, 'pre_page': page, 'next_page': page + 2,
            'page_list': range(1, total_page + 1), 'cur_page': page + 1}


@render_to('me/posts.html')
def posts(request, id, page=1, obj="from"):
    ''' 分页显示与用户有关的所有评论
    obj = 'from', 表示用戶发表的评论
    obj = 'to', 表示评论用戶的评论
    '''

    page = int(page) - 1
    error = ''
    total_page = 0

    try:
        owner = User.objects.get(pk=id)
    except User.DoesNotExist:
        url = reverse ('account:user_not_exist', args=[id])
        return HttpResponseRedirect(url)

    if page < 0:
        posts = []
        error = u'第 %s 页主题不存在!' % (page + 1)
    else:
        start = page * 10
        end = page * 10 + 10

        if obj == 'from':
            posts = Post.objects.filter(user=id).order_by('-updated')
        elif obj == 'to':
            posts = Post.objects.filter(touser=id).order_by('-updated')

        total_page = len(posts) / 10 + 1
        if ( page * 10 ) > len(posts):
            error = u'第 %s 页评论不存在!' % (page + 1)
            posts = []
        else:
            posts = posts[start:end]

    if obj == 'from':
        title = u'%s 发表的评论' % owner.username
    elif obj == 'to':
        title = u'%s 得到的评论' % owner.username

    page_list = range(1, total_page + 1) if total_page > 1 else []
    return {'title': title, 
            'owner': owner, 'owner_id': id, 'posts': posts, 'obj': obj,
            'error': error, 'last_page': total_page, 'pre_page': page, 'next_page': page + 2,
            'page_list': page_list, 'cur_page': page + 1}

