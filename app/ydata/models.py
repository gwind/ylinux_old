# coding: utf-8

# 将 YLinux.org 的主要数据结构在此定义

import os, re, codecs, datetime
from django.conf import settings
#from django.core.urlresolvers import reverse

from account.models import User,Group
from django.db import models

from ydata import settings as ydata_settings
from ydata.util import urlize,smiles
from markdown import Markdown


TZ_CHOICES = [(float(x[0]), x[1]) for x in (
    (-12, '-12'), (-11, '-11'), (-10, '-10'), (-9.5, '-09.5'), (-9, '-09'),
    (-8.5, '-08.5'), (-8, '-08 PST'), (-7, '-07 MST'), (-6, '-06 CST'),
    (-5, '-05 EST'), (-4, '-04 AST'), (-3.5, '-03.5'), (-3, '-03 ADT'),
    (-2, '-02'), (-1, '-01'), (0, '00 GMT'), (1, '+01 CET'), (2, '+02'),
    (3, '+03'), (3.5, '+03.5'), (4, '+04'), (4.5, '+04.5'), (5, '+05'),
    (5.5, '+05.5'), (6, '+06'), (6.5, '+06.5'), (7, '+07'), (8, '+08'),
    (9, '+09'), (9.5, '+09.5'), (10, '+10'), (10.5, '+10.5'), (11, '+11'),
    (11.5, '+11.5'), (12, '+12'), (13, '+13'), (14, '+14'),
)]

SIGN_CHOICES = ( 
    (1, 'PLUS'),
    (-1, 'MINUS'),
)

MARKUP_CHOICES = ( 
    ('bbcode', 'bbcode'),
    ('markdown', 'markdown'),
)

PRIVACY_CHOICES = ( 
    (0, u'Display your e-mail address.'),
    (1, u'Hide your e-mail address but allow form e-mail.'),
    (2, u'Hide your e-mail address and disallow form e-mail.'),
)


# Category 下分很多 Catalog
class Catalog(models.Model):
    # parent 键可以搜索 child
    parent = models.ForeignKey('self', blank=True, null=True, verbose_name='Catalog', related_name='child')
    name = models.CharField('名字', max_length=30)
    summary = models.CharField('概述', max_length=80)
    groups = models.ManyToManyField(Group, blank=True,
               verbose_name="只有在组中的用户可以访问此目录")
    position = models.IntegerField('位置', blank=True, 
               default=0, help_text="决定目录排序，默认0")
    description = models.TextField('描述', blank=True, 
                                   default='')
    # auto_now_add 在 create object 自动保存为当前时间
    # auto_now 在每次 save object 都自动保存为当前时间
    created = models.DateTimeField("创建时间", 
               auto_now_add=True)
    updated = models.DateTimeField("更新时间", auto_now=True)
    post_count = models.IntegerField('总帖子数', 
               blank=True, default=0)
    topic_count = models.IntegerField('总主题数', 
               blank=True, default=0)
    last_post = models.ForeignKey('Post', blank=True, 
               null=True, related_name='last_catalog_post')
    # There should be many topics here! FIXME!
    last_topic = models.ForeignKey('Topic', blank=True, 
               null=True, related_name='last_catalog_topic')
    class Meta:
        ordering = ['position']
        verbose_name = '目录'
        verbose_name_plural = '目录'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('wiki:show_catalog', [self.id])

    @property
    def children(self):
        return Catalog.objects.filter(parent=self.id)

    #@property
    #def posts(self):
    #    return Post.objects.filter(topic__catalog=self).select_related().count()

    def has_access(self, user):
        ''' 判断用户是否有权限，如果一个 Catalog 还未指定用户组，所有用户都有权限 '''
        if self.groups.count() > 0:
            if user.is_authenticated():
                try:
                    self.groups.get(user__pk=user.id)
                except Group.DoesNotExist:
                    return False
            else:
                return False
        return True


# 主题：每个 catalog 下会有很多主题，
# YLinux 默认： 论坛以 Topic 为表现形式，Wiki 以 Tag 为表现形式。
class Topic(models.Model):
    catalog = models.ForeignKey(Catalog, related_name='topics', verbose_name='Catalog')
    # 预计修改为 Subject
    name = models.CharField('标题', max_length=256)
    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated')
    user = models.ForeignKey(User, related_name='topics', verbose_name='User')
    user_ip = models.IPAddressField('User IP', blank=True, null=True)
    # 己弃用!!! 现使用 view_count
    views = models.IntegerField('查看次数', blank=True, default=0)
    # sticky 置顶属性
    sticky = models.BooleanField('Sticky', blank=True, default=False)
    # distillate ['distilit;'distəlit] n. 蒸馏物，馏份，精华
    distillate = models.BooleanField('精华', blank=True, default=False)
    # closed 禁止回复
    closed = models.BooleanField('关闭', blank=True, default=False)
    bloged = models.BooleanField('Blog中显示', default=True)
    wikied = models.BooleanField('Wiki中显示', default=True)
    forumed = models.BooleanField('Forum中显示', default=True)
    recycled = models.BooleanField('放入回收站', default=False)
    hidden = models.BooleanField('隐藏', default=False)
    markup = models.CharField('Markup', max_length=16, default="markdown", choices=MARKUP_CHOICES,
                              help_text='<span><a href="/wiki/topic/8/" target="_blank">Markdown 标记语言使用帮助</a></span>')

    # 没有被被关注，需要主动关注
    subscribers = models.ManyToManyField(User, related_name='subscriptions', verbose_name='Subscribers', blank=True)

    # Tags
    tags = models.ManyToManyField('Tag', blank=True, verbose_name="标签")
    view_count = models.IntegerField('查看次数', blank=True, default=0)
    post_count = models.IntegerField('回复数', blank=True, default=0)
    last_post = models.ForeignKey('Post', related_name='last_topic_post', blank=True, null=True)

    class Meta:
        ordering = ['-updated']
        verbose_name = '主题'
        verbose_name_plural = '主题'

    def __unicode__(self):
        return self.name

    @property
    def body_path(self):
        return os.path.join(settings.MEDIA_ROOT,
                            ydata_settings.TOPICS_DIR,
                            str(self.id) + '.src')

    @property
    def body_html_path(self):
        return os.path.join(settings.MEDIA_ROOT,
                            ydata_settings.TOPICS_DIR,
                            str(self.id) + '.html')
    
    @property
    def body(self):
        try:
            f = file(self.body_path, 'r')
            txt = f.read()
            f.close()
        except IOError:
            return ''
        return txt

    @property
    def body_html(self):
        self.view_count += 1
        self.save()

        try:
            f = file(self.body_html_path, 'r')
            html = f.read()
            f.close()
        except IOError:
            return ''
        return html

    @property
    def body_desc(self):
        return ''.join(self.body.split('\n')[:5])

    @property
    def feed_desc(self):
        return ''.join(self.body.split('\n')[:4])

    def save_file(self, text):
        dirname = os.path.dirname(self.body_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)	
        f = file(self.body_path, 'w')
        f.write(text)
        f.close()

        Markdown(extensions=['fenced_code']).convertFile(input=self.body_path, 
                       output=self.body_html_path, 
                       encoding="utf8", myfilter=ylinux_text_filter)

    @models.permalink
    def get_absolute_url(self):
        return ('wiki:show_topic', [self.id])

    def update_read(self, user):
        tracking = user.posttracking
        #if last_read > last_read - don't check topics
        if tracking.last_read and (tracking.last_read > self.last_post.created):
            return
        if isinstance(tracking.topics, dict):
            #clear topics if len > 5Kb and set last_read to current time
            if len(tracking.topics) > 5120:
                tracking.topics = None
                tracking.last_read = datetime.now()
                tracking.save()
            #update topics if exist new post or does't exist in dict
            if self.last_post.id > tracking.topics.get(str(self.id), 0):
                tracking.topics[str(self.id)] = self.last_post.id
                tracking.save()
        else:
            #initialize topic tracking dict
            tracking.topics = {self.id: self.last_post.id}
            tracking.save()


class Post(models.Model):
    topic = models.ForeignKey(Topic, related_name='posts', verbose_name='Topic')
    # parent 是 Post 间的继承关系
    parent = models.ForeignKey('self', blank=True, null=True, verbose_name='Post', related_name='child')
    user = models.ForeignKey(User, related_name='posts', verbose_name='User')
    touser = models.ForeignKey(User, blank=True, null=True, related_name='from_posts', verbose_name='ToUser')
    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated')
    markup = models.CharField('Markup', max_length=15, default="markdown", choices=MARKUP_CHOICES)
    body = models.TextField('正文')
    body_html = models.TextField('HTML正文')
    #body_text = models.TextField('Text version')
    user_ip = models.IPAddressField('User IP', blank=True, null=True)

    @property
    def feed_desc(self):
        return ''.join(self.body.split('\n')[:4])

    class Meta:
        ordering = ['created']
        get_latest_by = 'created'
        verbose_name = '回复'
        verbose_name_plural = '回复'

    def save(self, *args, **kwargs):
        if self.markup == 'bbcode':
            self.body_html = bbmarkup.bbcode(self.body)
        #elif self.markup == 'markdown' and MARKDOWN_AVAILABLE:
        elif self.markup == 'markdown':
            self.body_html = unicode(Markdown(self.body, safe_mode='escape'))
            #self.body_html = markdown(self.body, 'safe')
        elif self.markup == 'none':
            #self.body_html = self.body
            self.body_html = Markdown(extensions=['fenced_code']).convert(ylinux_text_filter(self.body))
        else:
            raise Exception('Invalid markup property: %s' % self.markup)
        #self.body_text = strip_tags(self.body_html)
        self.body_html = urlize(self.body_html)
        if ydata_settings.SMILES_SUPPORT:
            self.body_html = smiles(self.body_html)

        if not self.updated:
            self.updated = datetime.datetime.now()

        self.touser = self.parent.user if self.parent else self.topic.user

        super(Post, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self_id = self.id
        catalog = self.topic.catalog
        topic = self.topic
        self.last_topic_post.clear()
        self.last_catalog_post.clear()
        super(Post, self).delete(*args, **kwargs)
        try:
            topic.last_post = Post.objects.filter(topic=topic).latest()
        except Post.DoesNotExist:
            topic.last_post = None
        topic.post_count = Post.objects.filter(topic=topic).count()
        topic.save()
        try:
            catalog.last_post = Post.objects.filter(topic__catalog=catalog).latest()
        except Post.DoesNotExist:
            catalog.last_post = None
        catalog.post_count = Post.objects.filter(topic__catalog=catalog).count()
        catalog.topic_count = Topic.objects.filter(catalog=catalog).count()
        catalog.save()

    @models.permalink
    def get_absolute_url(self):
        return ('wiki:show_post', [self.id])


    @property
    def children(self):
        return Post.objects.filter(parent=self.id)


    def summary(self):
        LIMIT = 30
        tail = len(self.body) > LIMIT and '...' or '' 
        return self.body[:LIMIT] + tail

    __unicode__ = summary


# 声望
class Reputation(models.Model):
    from_user = models.ForeignKey(User, related_name='reputations_from', verbose_name='From')
    to_user = models.ForeignKey(User, related_name='reputations_to', verbose_name='To')
    topic = models.ForeignKey(Topic, related_name='topic', verbose_name='Topic')
    time = models.DateTimeField('Time', blank=True)
    sign = models.IntegerField('Sign', choices=SIGN_CHOICES, default=0)
    reason = models.TextField('Reason', blank=True, default='', max_length=1000)

    class Meta:
        verbose_name = 'Reputation'
        verbose_name_plural = 'Reputations'

    def __unicode__(self):
        return u'T[%d], FU[%d], TU[%d]: %s' % (self.topic.id, self.from_user.id, self.to_user.id, unicode(self.time))


# 举报
class Report(models.Model):
    reported_by = models.ForeignKey(User, related_name='reported_by', verbose_name='Reported by')
    post = models.ForeignKey(Post, verbose_name='Post')
    zapped = models.BooleanField('Zapped', blank=True, default=False)
    zapped_by = models.ForeignKey(User, related_name='zapped_by', blank=True, null=True,  verbose_name='Zapped by')
    created = models.DateTimeField('Created', blank=True)
    reason = models.TextField('Reason', blank=True, default='', max_length='1024')

    class Meta:
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'

    def __unicode__(self):
        return u'%s %s' % (self.reported_by ,self.zapped)


# 附件
class Attachment(models.Model):
    user = models.ForeignKey(User, related_name='attachments', verbose_name='User')
    topic = models.ForeignKey(Topic, related_name='attachments', verbose_name='Topic')
    name = models.TextField('Name')
    size = models.IntegerField('Size')
    path = models.CharField('Path', max_length=256)
    hash = models.CharField('Hash', max_length=40, blank=True, default='', db_index=True)
    description = models.TextField('描述', blank=True,  default='')
    qtimes = models.IntegerField('引用次数', blank=True, default=1) #被其他用户引用的次数
    dtimes = models.IntegerField('下载次数', blank=True, default=0) #被下载的次数
    created = models.DateTimeField("创建时间", auto_now_add=True)
    updated = models.DateTimeField("更新时间", auto_now=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('ydata:show_attachment', [self.id])

    @models.permalink
    def get_absolute_durl(self):
        return ('ydata:download_attachment', [self.id])

    def get_absolute_path(self):
        return os.path.join(settings.MEDIA_ROOT, ydata_settings.ATTACHMENT_UPLOAD_TO,
                            self.path)


class Tag(models.Model):
    ''' Tag 模型 '''
    
    name = models.CharField('Name', max_length=256)
    user = models.ForeignKey(User, related_name='tags', verbose_name='User')
    created = models.DateTimeField('Created', auto_now_add=True)
    total_ref = models.IntegerField(blank=True, default=0)

    def __unicode__(self):
        return self.name 


# TOPIC 里几种可行的引用附件格式： 
# [A:ID] | [a:ID] | [附:ID] | [附件:ID] 等
ATTACHMENT_QUOTE = re.compile(u'\[[ ]*(a|atta|attachment|附|附件)[ ]*:[ ]*(?P<id>[0-9]+)[ ]*\]', re.I)
WIKI_QUOTE = re.compile(u'\[[ ]*(w|wiki|维科|知识库)[ ]*:[ ]*(?P<id>[0-9]+)[ ]*\]', re.I)
IMG_QUOTE = re.compile(u'\[[ ]*(i|img|图片)[ ]*:[ ]*(?P<id>[0-9]+)[ ]*\]', re.I)

def ylinux_text_filter(text):

    # 过滤附件信息
    while 1:
        m = ATTACHMENT_QUOTE.search(text)
        if m:
            place_html = u''
            id = ''
            if m.group('id'):
                id = m.group('id')
                try:
                    a = Attachment.objects.get(pk=id)
                    place_html = u'<a href="%s" target="_blank">%s</a>' % (a.get_absolute_url(), a.name)
                except Attachment.DoesNotExist:
                    place_html = u'<span style="color:red;">[ID为%s的附件不存在]</span>' % id

            text = '%s%s%s' % (text[:m.start()], place_html, text[m.end():])
        else:
            break

    # 过滤WIKI信息
    while 1:
        m = WIKI_QUOTE.search(text)
        if m:
            place_html = u''
            id = ''
            if m.group('id'):
                id = m.group('id')
                try:
                    t = Topic.objects.get(pk=id)
                    place_html = u'<a href="%s" target="_blank">%s</a>' % (t.get_absolute_url(), t.name)
                except Topic.DoesNotExist:
                    place_html = u'<span style="color:red;">[ID为%s的附件不存在]</span>' % id

            text = '%s%s%s' % (text[:m.start()], place_html, text[m.end():])
        else:
            break

    # 过滤图片信息
    while 1:
        m = IMG_QUOTE.search(text)
        if m:
            place_html = u''
            id = ''
            if m.group('id'):
                id = m.group('id')
                try:
                    img = Attachment.objects.get(pk=id)
                    place_html = u'<img src="%s" alt="%s"/>' % (img.get_absolute_durl(), img.name)
                except Topic.DoesNotExist:
                    place_html = u'<span style="color:red;">[ID为%s的附件不存在]</span>' % id

            text = '%s%s%s' % (text[:m.start()], place_html, text[m.end():])
        else:
            break

    return text
