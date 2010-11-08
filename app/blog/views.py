# coding: utf-8

from account.models import User
from ydata.models import Topic, Post
from ydata.util import render_to, build_form, get_parents



@render_to('blog/index.html')
def index(request):

    print 'Here'
    return {'title':'YLinux Blog'}


@render_to('blog/homepage.html')
def homepage(request, id):
    ''' 指定 id 的用户 Blog 首页 '''

    print 'Here'
    try:
        user = User.objects.get(pk=id)
    except User.DoesNotExist:
        url = reverse ('account:user_not_exist', args=[id])
        return HttpResponseRedirect(url)

    topics = Topic.objects.filter(user=id).order_by('-updated')
    posts = Post.objects.filter(user=id).order_by('-updated')

    return {'the_user':user, 'topics':topics, 'posts':posts}

