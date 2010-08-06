# coding: utf-8

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden

#from account.decorators import login_required, permission_required
from account.models import User,AnonymousUser,Register
from account.forms import RegisterForm,LoginForm,AuthenticationForm, RequestRegisterForm

from ydata.models import Topic, Post

from ydata.util import render_to, build_form, get_parents


@render_to('account/index.html')
def index(request):

    return {'title':'用户主页', 'new_user':User.objects.all().order_by('-date_joined')[0]}


@render_to('account/login.html')
def login(request):

    print 'Here1'
    if request.method == "POST":
        print 'Here2'
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            print 'Here3'
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            from account import authenticate,login
            print 'Here4'
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if request.session.test_cookie_worked():
                        request.session.delete_test_cookie()
                        return HttpResponseRedirect(request.session.get('login_redirect_url','/') or '/')
                else:
                    return HttpResponseForbidden(u'用户未被激活，请联系管理员： ylinux.admin@gmail.com')

    else:
        # 形如 "http://127.0.0.1:8000/account/login?next=/admin/" 的 url 可以得到 next 值
        request.session['login_redirect_url'] = request.GET.get('next')
        form = AuthenticationForm(request)

    # 登录失败，或者第一次登录，都会到这里。form可以定制很多值
    request.session.set_test_cookie()
    return {'title':'登录', 'form':form}



# 退出后跳转到主页
#@login_required
def logout(request):
    #from django.contrib.auth import logout
    from account import logout
    previous_url = request.GET.get('next')
    logout(request)
    return HttpResponseRedirect(previous_url or '/')


@render_to('account/request_register.html')
def request_register(request):
    ''' 使用 email 申请一个注册 URL '''

    form = build_form (RequestRegisterForm, request)

    if form.is_valid():
        email = form.cleaned_data['email']
        try:
            register = Register.objects.get(email=email)
            return {'ALREADY_USED_EMAIL':True, 'email':email,
                    'REASON':'不要使用同一个 Email 重复申请注册！'}
        except Register.DoesNotExist:
            pass

        try:
            user = User.objects.get(email=email)
            return {'ALREADY_USED_EMAIL':True, 'email':email,
                    'REASON':'该用户已经成功加入 YLinux ！'}
        except User.DoesNotExist:
            pass

        register=Register.objects.create_profile(email)
        if register:
            #register.send_activation_email()
            url= "http://ylinux.org/account/register/%s" % register.activation_key

        return {'EMAIL_SENT':True, 'email':email, 'register_url':url}

    return {'NEW_REQUEST':True, 'form':form}
 

def register(request, key=None):
    """用户注册视图，根据用户名和Email信息注册新用户。 """

    try:
        register = Register.objects.get(activation_key=key)
    except Register.DoesNotExist:
        return HttpResponseForbidden(u'<h1>错误的 Key ： %s </h1>' % key)

    form = build_form (RegisterForm, request)

    if form.is_valid():
        # 从 POST 取得用户名，判断是否已存在
        username = form.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
            return render_to_response("account/register_failed.html",
                                      {"title":"注册失败","username":username,
                                       "error_type":"username",},
                                      context_instance=RequestContext(request))
        except User.DoesNotExist:
            pass

        # 从 POST 取得 password
        password_first = form.cleaned_data['password_first']
        password_second = form.cleaned_data['password_second']
        if not password_first == password_second:
            return render_to_response("account/register_failed.html",
                                      {"title":"注册失败","username":username,
                                       "error_type":"密码不匹配",},
                                      context_instance=RequestContext(request))

        print 'email: ', register.email
        user = Register.objects.create_activate_user (
            username=username, 
            email=register.email,
            password=password_first,
            activation_key=key )
        #User.objects.create_user(username=username, email=register.email, password=password_first)
        # 注册成功
        return render_to_response("account/register_successful.html",
                                  {"title":"注册成功","username":username},
                                  context_instance=RequestContext(request))

    # 打开注册页面
    return render_to_response("account/register.html",
                              { 'form': form },
                              context_instance=RequestContext(request))


@render_to('account/user.html')
def user(request, id):

    try:
        user = User.objects.get(pk=id)
    except User.DoesNotExist:
        url = reverse ('account:user_not_exist', args=[id])
        return HttpResponseRedirect(url)

    topics = Topic.objects.filter(user=id).order_by('-updated')
    posts = Post.objects.filter(user=id).order_by('-updated')

    # 因为 ylinux.app.sessions.middleware.SessionMiddleware
    # 中间件会在 request 里的设置 user 变量，我们这里另起名
    return {'the_user':user, 'topics':topics, 'posts':posts}

@render_to('account/list_all_user.html')
def list_all_user(request):

    ''' 列出已注册的用户，还未最终决定是否需要这个功能 '''
