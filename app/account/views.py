# coding: utf-8

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse

from account.models import User,AnonymousUser
from account.forms import RegisterForm,LoginForm,AuthenticationForm


def login(request):

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            from account import authenticate,login
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                login(request, user)
                if request.session.test_cookie_worked():
                    request.session.delete_test_cookie()
                return HttpResponseRedirect(request.session.get('previous_url','/'))

    else:
        request.session['previous_url'] = request.META.get('HTTP_REFERER', '/')
        form = AuthenticationForm(request)

    # 登录失败，或者第一次登录，都会到这里。form可以定制很多值
    request.session.set_test_cookie()
    return render_to_response('account/login.html',
        {'title':'登录','form': form,},
        context_instance=RequestContext(request))



# 退出后跳转到主页
def logout(request):
    from django.contrib.auth import logout
    logout(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def register(request):
    """用户注册视图，根据用户名和Email信息注册新用户。
    """

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 从 POST 取得用户名，判断是否已存在
            username = form.cleaned_data['username']
            try:
                old_user = User.objects.get(username=username)
            except User.DoesNotExist:
                old_user = None
            if old_user:
                return render_to_response("account/register_failed.html",
                        {"title":"注册失败","username":username,
                         "error_type":"username",},
                         context_instance=RequestContext(request))

            # 从 POST 取得 password
            password_first = form.cleaned_data['password_first']
            password_second = form.cleaned_data['password_second']
            if not password_first == password_second:
                return render_to_response("account/register_failed.html",
                        {"title":"注册失败","username":username,
                         "error_type":"密码不匹配",},
                         context_instance=RequestContext(request))

            # 从 POST 取得 email
            email = form.cleaned_data['email']
            if not email:
                return render_to_response("account/register_failed.html",
                        {"title":"注册失败","username":username,
                         "error_type":"email",},
                         context_instance=RequestContext(request))

            #用户名和Email都没有重复，就注册新用户
            new_user = User.objects.create_user(username, email, password_first)
            #new_user = User(username = username, password = password_first)
            new_user.save()
            return render_to_response("account/register_successful.html",
                                      {"title":"注册成功","username":username},
                                      context_instance=RequestContext(request))

    else:
        form = RegisterForm()
    
    return render_to_response("account/register.html",
                              { 'form': form },
                              context_instance=RequestContext(request))

