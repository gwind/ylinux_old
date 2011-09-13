# Django settings for ylinux project.
# coding: utf-8

import os.path
import sys 
import re

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

# lib 目录安放第三方软件包
if sys.path.count(PROJECT_ROOT+"/lib") == 0:
    sys.path.insert(0,PROJECT_ROOT+"/lib")

# app 目录存放我的project包含的软件包
if sys.path.count(PROJECT_ROOT+"/app") == 0:
    sys.path.insert(0,PROJECT_ROOT+"/app")

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DOMAIN = "127.0.0.1:8000"

INTERNAL_IPS = ('127.0.0.1',)

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

# 这里填写你的发邮件email账户名和密码
DEFAULT_FROM_EMAIL = ''
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = ''
EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = '[YLinux]'


MANAGERS = ADMINS

# 数据库
# 示例使用 mysql 数据库
DATABASES = {
    'default': {
        # 可选数据库: postgresql_psycopg2 postgresql mysql sqlite3 oracle
        'ENGINE': 'django.db.backends.mysql',
        #'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'ylinux',
        'USER': 'ylinux',
        'PASSWORD': '123456',
        'HOST': '',
        'PORT': '',
        }
    }


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-cn'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True


MEDIA_ROOT = PROJECT_ROOT+'/ymedia/'
MEDIA_URL = '/ymedia/'


# Make this unique, and don't share it with anybody.
SECRET_KEY = 'c#0cz^i$lyr6*b*xe-t@0tqc_c3dnju=+c1lk^k7(r^7lhz$g@'


# YLinux 后端认证模块，这是一个tuple，可以有多种后段认证技术，
# 只要有一个成功即可。详细说明请看 ylinux.app.accout 
AUTHENTICATION_BACKENDS = ('ylinux.app.account.backends.ModelBackend',)
LOGIN_URL = '/account/login/'
LOGOUT_URL = '/account/logout/'
LOGIN_REDIRECT_URL = '/account/profile/'

# 定义如何加载模板，本处只在指定目录加载

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    #'django.template.loaders.filesystem.load_template_source',
    #'django.template.loaders.app_directories.load_template_source',
    #'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
#    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'ylinux.app.sessions.middleware.SessionMiddleware',
    'ylinux.app.account.middleware.AuthenticationMiddleware',
)

#ROOT_URLCONF = 'ylinux.urls'
ROOT_URLCONF = 'urls'

# 指定模板目录

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    PROJECT_ROOT+"/templates",
)

# 模板处理器

TEMPLATE_CONTEXT_PROCESSORS = (
#    "django.core.context_processors.auth",

    #auth返回user对象
    "ylinux.app.account.context_processors.auth",

    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
)

INSTALLED_APPS = (
#    'django.contrib.auth',
    # 目前 account 里的 ContentType 需要这个models
    'django.contrib.contenttypes',
#    'django.contrib.sessions',
#    'django.contrib.sites',
#    'django.contrib.admin',

    # Ylinux.org 的应用
    'ylinux.app.sessions',
    'ylinux.app.admin',
    'ylinux.app.account',
    'ylinux.app.home',
    'ylinux.app.ydata',
    'ylinux.app.wiki',
    'ylinux.app.blog',
    'ylinux.app.ylab',
    'ylinux.app.me',
    'django_xmlrpc',
)


# 语言集合
LANGUAGES = (
    ('en', 'English'),
    ('zh-cn', '简体中文'),
    ('zh-tw', '繁体中文'),
)

# XML-RPC Public interface for YLinux
XMLRPC_DEBUG=True
#XMLRPC_METHODS = ylinux_xmlrpc.XMLRPC_METHODS
XMLRPC_METHODS = (
    ('ylinux_xmlrpc.list_all_topic', 'list_all_topic'),
    ('ylinux_xmlrpc.add_topic', 'add_topic'),
    ('ylinux_xmlrpc.show_topic', 'show_topic'),
    ('ylinux_xmlrpc.delete_topic', 'delete_topic'),
    ('ylinux_xmlrpc.delete_all_topic', 'delete_all_topic'),

)
