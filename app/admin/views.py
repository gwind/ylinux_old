# coding: utf-8

from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse

from account.decorators import login_required, permission_required

from account.models import Permission,Group,User,AnonymousUser
from ydata.models import Catalog,Topic,Post

from account.forms import RegisterForm,LoginForm,AuthenticationForm
from admin.forms import \
    AddUserForm, EditUserForm, \
    AddGroupForm, EditGroupForm, \
    AddCatalogForm, EditCatalogForm, \
    AddPermissionForm, EditPermissionForm

from ydata.util import render_to, build_form, get_parents


# 视图是 MVC 里面的 V
# 这里的视图设计原则尽量如下：
# 1. show_OBJECT 显示OBJECT
# 2. edit_OBJECT 编辑OBJECT
# 3. del_OBJECT 删除OBJECT
# 4. add_OBJECT 新建OBJECT
#
# 单独 /OBJECT/ 显示这一类
#
# show 不需要权限，其他权限最好再做区分


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
# show, edit, add, del
@permission_required('account.view_perm')
@render_to ('admin/permission.html')
def permission(request):

    permissions = Permission.objects.all()
    if hasattr(request, 'user'):
        create_perm = request.user.has_perm ('account.create_perm')
        edit_perm = request.user.has_perm ('account.edit_perm')
        delete_perm = request.user.has_perm ('account.delete_perm')
    return {'permissions':permissions, 
            'create_perm':create_perm,
            'edit_perm':edit_perm,
            'delete_perm':delete_perm}


@permission_required('account.create_perm', login_url='/admin/login')
@render_to ('admin/add_permission.html')
def add_permission(request):

    form = build_form (AddPermissionForm, request)
    if form.is_valid():
        permission = form.save()
        url = reverse ('admin:show_permission', args=[permission.id])
        return HttpResponseRedirect(url)

    return {'form':form}


@permission_required('account.view_perm')
@render_to ('admin/show_permission.html')
def show_permission (request, id):

    permission = get_object_or_404 (Permission, pk=id)
    return {'permission':permission}


@permission_required('account.edit_perm')
@render_to ('admin/edit_permission.html')
def edit_permission (request, id):

    permission = get_object_or_404(Permission, pk=id)
    
    form = build_form (EditPermissionForm, request, instance=permission)

    if form.is_valid():
        form.save()
        url = reverse ('admin:show_permission', args=[id])
        return HttpResponseRedirect(url)

    return {'form':form, 'permission':permission}


@permission_required('account.delete_perm')
@render_to ('admin/del_permission.html')
def del_permission (request, id):

    permission = get_object_or_404 (Permission, pk=id)
    # 这里等待以后验证是否已有其他关联
    permission.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


# Group 管理
# show, add, edit, del

@permission_required('account.view_group')
@render_to('admin/group.html')
def group(request):

    groups = Group.objects.all()
    return {'groups':groups}


@permission_required('account.create_group')
@render_to('admin/add_group.html')
def add_group(request):

    form = build_form (AddGroupForm, request)
    if form.is_valid():
        group = form.save()
        url = reverse ('admin:show_group', args=[group.id])
        return HttpResponseRedirect(url)

    return {'form':form}


@permission_required('account.view_group')
@render_to ('admin/show_group.html')
def show_group (request, id):

    group = get_object_or_404 (Group, pk=id)
    return {'group':group}


@permission_required('account.edit_group')
@render_to ('admin/edit_group.html')
def edit_group (request, id):

    group = get_object_or_404(Group, pk=id)
    
    form = build_form (EditGroupForm, request, instance=group)

    if form.is_valid():
        form.save()
        url = reverse ('admin:show_group', args=[id])
        return HttpResponseRedirect(url)

    return {'form':form, 'group':group}


@permission_required('account.delete_group')
@render_to ('admin/del_group.html')
def del_group (request, id):

    group = get_object_or_404 (Group, pk=id)
    # 这里等待以后验证是否已有其他关联
    group.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


# User 管理

@permission_required('account.view_user')
@render_to('admin/user.html')
def user(request):

    users = User.objects.all()
    if hasattr(request, 'user'):
        create_user = request.user.has_perm ('account.create_user')
        edit_user =  request.user.has_perm ('account.edit_user')
        delete_user = request.user.has_perm ('account.delete_user')
    return {'users':users,
            'create_user':create_user,
            'edit_user':edit_user,
            'delete_user':delete_user}


@permission_required('account.view_user')
@render_to ('admin/show_user.html')
def show_user (request, id):

    user = get_object_or_404 (User, pk=id)
    return {'the_user':user}


@permission_required('account.create_user')
@render_to('admin/add_user.html')
def add_user(request):

    form = build_form (AddUserForm, request)
    if form.is_valid():
        user = form.save()
        url = reverse ('admin:show_user', args=[user.id])
        return HttpResponseRedirect(url)

    return {'form':form}


@permission_required('account.edit_user')
@render_to ('admin/edit_user.html')
def edit_user (request, id):

    user = get_object_or_404(User, pk=id)
    form = build_form (EditUserForm, request, instance=user)

    if form.is_valid():
        form.save()
        url = reverse ('admin:show_user', args=[id])
        return HttpResponseRedirect(url)

    return {'form':form, 'user':user}


# 这里用一个冒险的技巧，权限为'just_admin_can_delete'的
# 就可以删除用户，但是这只有 superuser 可以验证为 True 
@permission_required('just_admin_can_delete')
@render_to ('admin/del_user.html')
def del_user (request, id):

    user = get_object_or_404 (User, pk=id)
    # 这里等待以后验证是否已有其他关联
    user.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


# Catalog 管理
@permission_required('ydata.view_catalog')
@render_to ('admin/catalog.html')
def catalog (request):
    catalogs = Catalog.objects.filter(parent=None)
    if hasattr(request, 'user'):
        create_catalog = request.user.has_perm ('ydata.create_catalog')
        edit_catalog = request.user.has_perm ('ydata.edit_catalog')
        delete_catalog = request.user.has_perm ('ydata.delete_catalog')

    return {'catalogs':catalogs,
            'create_catalog':create_catalog,
            'edit_catalog':edit_catalog,
            'delete_catalog':delete_catalog}


# 显示指定 id 的 Catalog
@permission_required('ydata.view_catalog')
@render_to ('admin/show_catalog.html')
def show_catalog (request, id):

    catalog = get_object_or_404 (Catalog, pk=id)
    subcatalogs = Catalog.objects.filter(parent=id)
    parents = get_parents (Catalog, id)
    if hasattr(request, 'user'):
        create_catalog = request.user.has_perm ('ydata.create_catalog')
        edit_catalog = request.user.has_perm ('ydata.edit_catalog')
        delete_catalog = request.user.has_perm ('ydata.delete_catalog')
    return {'catalog':catalog, 'parents':parents,
            'subcatalogs':subcatalogs,
            'create_catalog':create_catalog,
            'edit_catalog':edit_catalog,
            'delete_catalog':delete_catalog}


@permission_required('ydata.create_catalog')
@render_to('admin/add_catalog.html')
def add_catalog(request, parent_id=None):

    if parent_id:
        catalog = get_object_or_404 (Catalog, pk=parent_id)
        parents = get_parents (Catalog, catalog.id)

        form = build_form (AddCatalogForm, request, parent=catalog)
    
    else:
        form = build_form (AddCatalogForm, request)

    if form.is_valid():
        catalog = form.save()
        url = reverse ('admin:show_catalog', args=[catalog.id])
        return HttpResponseRedirect (url)

    if parent_id:
        return {'catalog': catalog,
                'form': form,
                'parents': parents,}
    else:
        return {'form':form}


@permission_required('ydata.edit_catalog')
@render_to('admin/edit_catalog.html')
def edit_catalog(request, id):

    catalog = get_object_or_404(Catalog, pk=id)
    parents = get_parents (Catalog, id)
    
    form = build_form (EditCatalogForm, request,
                       parent=catalog.parent,
                       instance=catalog)

    if form.is_valid():
        catalog = form.save()
        url = reverse ('admin:show_catalog', 
                       args=[catalog.id])
        return HttpResponseRedirect(url)

    return {'form':form,'parents':parents,'catalog':catalog}


@permission_required('ydata.delete_catalog')
@render_to ('admin/del_catalog.html')
def del_catalog (request, id):

    catalog = get_object_or_404 (Catalog, pk=id)
    subcatalogs = Catalog.objects.filter(parent=id)

    if subcatalogs:
        parents = get_parents (Catalog, id)
        return {'catalog':catalog, 'parents':parents,
                'subcatalogs':subcatalogs}

    catalog.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


# 重启 fastcgi
def reboot(request):

    import os
    user=os.popen('whoami').read().strip()
    os.system('killall -u %s' % user)

    return HttpResponseRedirect(reverse('home:index'))


# 注释

# 1. permission_required 的用法
# @permission_required('account.createe_perm', login_url='/admin/')
# login_url 指定认证失败的跳转路径
