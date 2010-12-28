#coding: utf-8

#from forms import ContactForm
from django.shortcuts import render_to_response
#from django.http import HttpResponseRedirect,HttpResponse
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


