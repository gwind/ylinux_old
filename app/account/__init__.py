# coding: utf-8

import datetime
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

SESSION_KEY = '_auth_user_id'
BACKEND_SESSION_KEY = '_auth_user_backend'
REDIRECT_FIELD_NAME = 'next'


def load_backend(path):
    """将 'django.contrib.auth.backends.ModelBackend' 形式转为路径，再用 import_module 得到对象。
    """

    # rfind 在字符串对象里查找某个字符(串)出现的最后位置
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured, 'Error importing authentication backend %s: "%s"' % (module, e)
    except ValueError, e:
        raise ImproperlyConfigured, 'Error importing authentication backends. Is AUTHENTICATION_BACKENDS a correctly defined list or tuple?'
    try:
        cls = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured, 'Module "%s" does not define a "%s" authentication backend' % (module, attr)
    return cls()

def get_backends():
    """ 从 settings.AUTHENTICATION_BACKENDS 里依次得到一个后端认证模块列表
    """
    from django.conf import settings
    backends = []
    for backend_path in settings.AUTHENTICATION_BACKENDS:
        backends.append(load_backend(backend_path))
    return backends

def authenticate(**credentials):
    """只要有一个后端认证模块通过，就返回User对象
    """
    for backend in get_backends():
        try:
            user = backend.authenticate(**credentials)
        except TypeError:
            # This backend doesn't accept these credentials as arguments. Try the next one.
            continue
        if user is None:
            continue
        # Annotate the user object with the path of the backend.
        user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        return user

def login(request, user):
    """
    Persist a user id and a backend in the request. This way a user doesn't
    have to reauthenticate on every request.
    """
    if user is None:
        user = request.user
    # TODO: It would be nice to support different login methods, like signed cookies.
    user.last_login = datetime.datetime.now()
    user.save()

    if SESSION_KEY in request.session:
        if request.session[SESSION_KEY] != user.id:
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
    else:
        request.session.cycle_key()
    request.session[SESSION_KEY] = user.id
    request.session[BACKEND_SESSION_KEY] = user.backend
    if hasattr(request, 'user'):
        request.user = user

def logout(request):
    """
    Removes the authenticated user's ID from the request and flushes their
    session data.
    """
    request.session.flush()
    if hasattr(request, 'user'):
        from account.models import AnonymousUser
        request.user = AnonymousUser()

def get_user(request):
    """在middleware里用来得到user对象
    """
    from account.models import AnonymousUser
    try:
        user_id = request.session[SESSION_KEY]
        backend_path = request.session[BACKEND_SESSION_KEY]
        backend = load_backend(backend_path)
        user = backend.get_user(user_id) or AnonymousUser()
    except KeyError:
        user = AnonymousUser()
    return user
