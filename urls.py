# coding: utf-8

try:
    import settings
except ImportError:
    import sys
    sys.stderr.write("import settting error!")
    sys.exit(1)


from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^ylinux/', include('ylinux.foo.urls')),
    # 注意 '' 和 ^$ 不同！
    (r'', include('ylinux.app.home.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #(r'^admin/', include(admin.site.urls)),
)


# 开发使用 django 自带的 web 服务器，需按照下面方法设置静态目录。如果放
# 到公网上，那么需要用你所有的 web 服务器设置静态目录。一般在共享主机的
# 环境里，针对 apache 可以用 .htaccess 实现

# 另外要注意的是，如果打开 admin 功能，就不要用 static 作为 url 前部分。

# 如果用 'show_indexes' 打开目录显示功能，可以在定义一个
# static/directory_index.html 模板。

if (settings.DEBUG):
    urlpatterns += patterns ('',
        (r'^ymedia/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )

