#coding: utf-8

#from forms import ContactForm
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect,HttpResponse
#from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from account.models import User
from ydata.models import Catalog, Topic, Post
from ydata.util import render_to, build_form, get_parents


@render_to('bbs/index.html')
def index(request):

    catalogs = Catalog.objects.filter(parent=None)

    all_user = User.objects.all()
    if all_user:
        new_register_user = all_user.order_by('-date_joined')[0]
    else:
        new_register_user = None

    return {'title':'论坛', 'catalogs':catalogs, 
            'new_register_user':new_register_user}


@render_to('bbs/catalog.html')
def catalog(request, id):

    try:
        catalog = Catalog.objects.get(pk=id)
    except Catalog.DoesNotExist:
        url = reverse ('bbs:forum_not_exist', args=[id])
        return HttpResponseRedirect(url)

    parents = get_parents (Catalog, id)
    topics = Topic.objects.filter(catalog=catalog)

    return {'catalog':catalog, 'parents':parents, 'topics':topics}

@render_to('bbs/topic.html')
def topic(request, id):

    try:
        topic = Topic.objects.get(pk=id)
    except Topic.DoesNotExist:
        url = reverse ('bbs:topic_not_exist', args=[id])
        return HttpResponseRedirect(url)

    parents = get_parents (Catalog, topic.catalog.id)
    posts = Post.objects.filter(topic=topic)

    return {'topic':topic, 'parents': parents, 'posts':posts}


# 一些 DoesNotExist 的页面这里处理
@render_to('bbs/DoesNotExist.html')
def doesnotexist(request, type, id):
    return {'type':type, 'id':id,}



@render_to('bbs/catalog_forum.html')
def catalog_forum(request, id):

    try:
        catalog = Catalog.objects.get(pk=id)
    except Catalog.DoesNotExist:
        url = reverse ('wiki:catalog_not_exist', args=[id])
        return HttpResponseRedirect(url)

    parents = get_parents (Catalog, id)
    catalogs = Catalog.objects.filter(parent=id)
    topics = Topic.objects.filter(catalog=id).exclude(hidden=1).exclude(recycled=1)
    return {'title':catalog.name, 'parents':parents, 'catalogs':catalogs, 'topics':topics}


