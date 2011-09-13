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
        user = User.objects.get(pk=id)
    except User.DoesNotExist:
        url = reverse ('account:user_not_exist', args=[id])
        return HttpResponseRedirect(url)

    topic_count = len(Topic.objects.filter(user=id).order_by('-updated'))
    post_count = len(Post.objects.filter(user=id).order_by('-updated'))
    fpost_count = len(Post.objects.filter(touser=id).order_by('-updated'))

    return {'title': u'欢迎访问 %s 的首页' % user.username, 
            'owner':user, 'owner_id': id, 
            'topic_count': topic_count, 'post_count': post_count, 'fpost_count': fpost_count}


@render_to('me/topics.html')
def topics(request, id):
    ''' 指定 id 的用户 ME HOME '''

    try:
        user = User.objects.get(pk=id)
    except User.DoesNotExist:
        url = reverse ('account:user_not_exist', args=[id])
        return HttpResponseRedirect(url)

    topics = Topic.objects.filter(user=id).order_by('-updated')[:10]

    return {'title': u'%s 发表的文章' % user.username, 
            'owner':user, 'owner_id': id, 'topics': topics}



@render_to('me/posts_by_other.html')
def posts_by_other(request, id):
    ''' 指定 id 的用户 ME HOME '''

    try:
        user = User.objects.get(pk=id)
    except User.DoesNotExist:
        url = reverse ('account:user_not_exist', args=[id])
        return HttpResponseRedirect(url)

    posts = Post.objects.filter(touser=id).order_by('-updated')[:10]

    return {'title': u'%s 得到的评论' % user.username, 
            'owner':user, 'owner_id': id, 'posts': posts}



@render_to('me/posts_for_other.html')
def posts_for_other(request, id):
    ''' 指定 id 的用户 ME HOME '''

    try:
        user = User.objects.get(pk=id)
    except User.DoesNotExist:
        url = reverse ('account:user_not_exist', args=[id])
        return HttpResponseRedirect(url)

    posts = Post.objects.filter(user=id).order_by('-updated')[:10]

    return {'title': u'%s 发表的评论' % user.username, 
            'owner':user, 'owner_id': id, 'posts': posts}

