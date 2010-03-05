# coding: utf-8

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse

from account.decorators import login_required

from account.models import Permission,Group,User,AnonymousUser
from ydata.models import Category,Catalog,Topic,Post

from account.forms import RegisterForm,LoginForm,AuthenticationForm
from admin.forms import CategoryForm,CatalogForm,UserForm,GroupForm,PermissionForm

from ydata.util import render_to,build_form

@login_required
@render_to('admin/index.html')
def index(request):

    """ 首页 """

    return {}


@render_to('admin/login.html')
def login(request):

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            from account import authenticate,login
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active and user.is_staff:
                login(request, user)
                if request.session.test_cookie_worked():
                    request.session.delete_test_cookie()
                return HttpResponseRedirect(request.session.get('previous_url','/'))

    else:
        request.session['previous_url'] = request.META.get('HTTP_REFERER', '/')
        form = AuthenticationForm(request)

    # 登录失败，或者第一次登录，都会到这里。form可以定制很多值
    request.session.set_test_cookie()
    return {'title':'登录','form': form,}


# Permission 管理

@render_to('admin/permission.html')
def permission(request, id):

    if id:
        try:
            permission = Permission.objects.get(pk=id) 
        except Permission.DoesNotExist:
            permission = None

        if request.method == 'POST':
            form = PermissionForm(data=request.POST)
            if form.is_valid() and permission:
                permission.name = form.cleaned_data['name']
                permission.codename = form.cleaned_data['codename']
                permission.save()
            return HttpResponseRedirect(reverse('admin:show_permissions'))

        form = PermissionForm(permission.__dict__)
        return {'permission':permission,'form':form}
            
    permissions = Permission.objects.all()
    return {'permissions':permissions}


# User 管理

@render_to('admin/user.html')
def user(request, id):

    if id:
        try:
            user = User.objects.get(pk=id) 
        except User.DoesNotExist:
            user = None

        if request.method == 'POST':
            form = UserForm(data=request.POST)
            if form.is_valid() and user:
                user.username = form.cleaned_data['username']
                user.save()
            return HttpResponseRedirect(reverse('admin:show_users'))

        form = UserForm(user.__dict__)
        return {'user':user,'form':form}
            
    users = User.objects.all()
    return {'users':users}

@render_to('admin/add_user.html')
def add_user(request):

    if request.method == 'POST':
        form = UserForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            try:
                old_user = User.objects.get(username=username)
            except User.DoesNotExist:
                old_user = None
            if old_user:
                return render_to_response("account/register_failed.html",
                        {"title":"注册失败","username":username,
                         "error_type":"username",},
                         context_instance=RequestContext(request))
            User.objects.create_user(username=username, email=email,password=password)
        return HttpResponseRedirect(reverse('admin:show_users'))

    form = UserForm()
    return {'form':form}


# Category 管理    
@render_to('admin/category.html')
def category(request, id):

    if id:
        try:
            category = Category.objects.get(pk=id)
        except Category.DoesNotExist:
            category = None

        if request.method == 'POST':
            form = CategoryForm(data=request.POST)
            if form.is_valid() and category:
                category.name = form.cleaned_data['name']
                category.position = form.cleaned_data['position']
                category.save()
            return HttpResponseRedirect(reverse('admin:show_categorys'))

        # 绑定数据的 Form，增加  value 选项值
        form = CategoryForm(category.__dict__)
        return {'category':category,'form':form}

    categorys = Category.objects.all()
    return {'categorys':categorys}


@render_to('admin/add_category.html')
def add_category(request):

    if request.method == 'POST':
        form = CategoryForm(data=request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            position = form.cleaned_data['position']
            category = Category(name=name,position=position)
            category.save()
        return HttpResponseRedirect(reverse('admin:show_categorys'))

    form = CategoryForm()
    return {'form':form}


# Catalog 管理

@render_to('admin/catalog.html')
def catalog(request,id):

    if id:
        try:
            catalog = Catalog.objects.get(pk=id)
        except Catalog.DoesNotExist:
            catalog = None

        if request.method == 'POST':
            form = CatalogForm(data=request.POST)
            if form.is_valid() and catalog:
                catalog.category = form.cleaned_data['category']
                catalog.name = form.cleaned_data['name']
                catalog.position = form.cleaned_data['position']
                catalog.description = form.cleaned_data['description']
                catalog.save()
            return HttpResponseRedirect(reverse('admin:show_catalogs'))

        form = CatalogForm(catalog.__dict__)
        return {'catalog':catalog,'form':form}

    catalogs = Catalog.objects.all()
    return {'catalogs':catalogs}


@render_to('admin/add_catalog.html')
def add_catalog(request):

    if request.method == 'POST':
        form = CatalogForm(data=request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            name = form.cleaned_data['name']
            position = form.cleaned_data['position']
            description = form.cleaned_data['description']
            catalog = Catalog(category=category,name=name,position=position,description=description)
            catalog.save()
        return HttpResponseRedirect(reverse('admin:show_catalogs'))

    form = CatalogForm()
    return {'form':form}


# 重启 fastcgi
def reboot(request):

    import os
    user=os.popen('whoami').read().strip()
    os.system('killall -u %s' % user)

    return HttpResponseRedirect(reverse('home:index'))
