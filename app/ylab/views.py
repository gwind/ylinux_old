# coding: utf-8

from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from syndication.views import Feed
from django.utils import simplejson

from account.decorators import login_required, permission_required
from ydata.models import Catalog,Topic,Post
from ydata.forms import AddPostForm, \
    AddTopicForm, EditTopicForm

from ydata.util import render_to, build_form, get_parents, ylinux_get_ip

import datetime

def time(request):
    js = u'<script type="text/javascript">parent.ajax_callback(0);parent.createUploadForm()</script>'
    current = datetime.datetime.now()
    return HttpResponse(`current` + js)


def upload_single_file(req):
    ''' 仅仅处理上传的文件中的第一个 '''

    if req.method != 'POST':
        return HttpResponse("Just for POST test!")

    url = '/ydata/attachement/3'
    attachment = req.FILES.values()[0]
    innerHTML = u'<span><a href="%s">%s</a>， %s， <a href="%s/delete">删除</a></span>' % (url, attachment.name, attachment.size, url)
    r = u'<script type="text/javascript">window.parent.AfterSubmit(%s);</script>' % innerHTML
    return HttpResponse(r)


def update_post_profile(req):
    
    posts = Post.objects.all()
    for p in posts:
        if p.parent:
            p.touser = p.parent.user
        else:
            p.touser = p.topic.user
        p.updated = p.created
        p.save()

    return HttpResponse(u'更新 posts 完成!')
