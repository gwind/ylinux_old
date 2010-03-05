# coding: utf-8

# 将 YLinux.org 的主要数据结构在此定义

from markdown import Markdown

from account.models import User,Group
from django.db import models

from ydata import settings as ydata_settings
from ydata.util import urlize,smiles


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


# 分类
class Category(models.Model):
    name = models.CharField('Name', max_length=80)
    groups = models.ManyToManyField(Group,blank=True, null=True, verbose_name='Groups', help_text='Only users from these groups can see this category')
    # position 可能是为了排列
    position = models.IntegerField('Position', blank=True, default=0)

    class Meta:
        ordering = ['position']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __unicode__(self):
        return self.name

    def catalog_count(self):
        return self.catalogs.all().count()

    @models.permalink
    def get_absolute_url(self):
        return ('wiki:show_category', [self.id])

    @property
    def topics(self):
        return Topic.objects.filter(catalog__category=self).select_related()

    @property
    def posts(self):
        return Post.objects.filter(topic__catalog__category=self).select_related()

    def has_access(self, user):
        if self.groups.count() > 0:
            if user.is_authenticated(): 
                try:
                    self.groups.get(user__pk=user.id)
                except Group.DoesNotExist:
                    return False
            else:
                return False
        return True


# Category 下分很多 Catalog
class Catalog(models.Model):
    category = models.ForeignKey(Category, related_name='catalogs', verbose_name='Category')
    name = models.CharField('Name', max_length=80)
    position = models.IntegerField('Position', blank=True, default=0)
    description = models.TextField('Description', blank=True, default='')
    moderators = models.ManyToManyField(User, blank=True, null=True, verbose_name='Moderators')
    updated = models.DateTimeField('Updated', auto_now=True)
    post_count = models.IntegerField('Post count', blank=True, default=0)
    topic_count = models.IntegerField('Topic count', blank=True, default=0)
    last_post = models.ForeignKey('Post', related_name='last_catalog_post', blank=True, null=True)

    class Meta:
        ordering = ['position']
        verbose_name = 'Catalog'
        verbose_name_plural = 'Catalogs'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('wiki:show_catalog', [self.id])

    @property
    def posts(self):
        return Post.objects.filter(topic__catalog=self).select_related()


# 主题：每个 catalog 下会有很多主题，
# YLinux 默认： 论坛以 Topic 为表现形式，Wiki 以 Tag 为表现形式。
class Topic(models.Model):
    catalog = models.ForeignKey(Catalog, related_name='topics', verbose_name='Catalog')
    # 预计修改为 Subject
    name = models.CharField('描述', max_length=255)
    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated', null=True)
    user = models.ForeignKey(User, verbose_name='User')
    views = models.IntegerField('查看次数', blank=True, default=0)
    sticky = models.BooleanField('Sticky', blank=True, default=False)
    closed = models.BooleanField('禁止回复', blank=True, default=False)
    subscribers = models.ManyToManyField(User, related_name='subscriptions', verbose_name='Subscribers', blank=True)
    post_count = models.IntegerField('Post count', blank=True, default=0)
    last_post = models.ForeignKey('Post', related_name='last_topic_post', blank=True, null=True)

    class Meta:
        ordering = ['-updated']
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'

    def __unicode__(self):
        return self.name

    @property
    def head(self):
        try:
            return self.posts.select_related().order_by('created')[0]
        except IndexError:
            return None

    @property
    def reply_count(self):
        return self.post_count - 1

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
    user = models.ForeignKey(User, related_name='posts', verbose_name='User')
    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated', blank=True, null=True)
    markup = models.CharField('Markup', max_length=15, default="markup", choices=MARKUP_CHOICES)
    body = models.TextField('Message')
    body_html = models.TextField('HTML version')
    #body_text = models.TextField('Text version')
    user_ip = models.IPAddressField('User IP', blank=True, null=True)


    class Meta:
        ordering = ['created']
        get_latest_by = 'created'
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def save(self, *args, **kwargs):
        if self.markup == 'bbcode':
            self.body_html = bbmarkup.bbcode(self.body)
        #elif self.markup == 'markdown' and MARKDOWN_AVAILABLE:
        elif self.markup == 'markdown':
            self.body_html = unicode(Markdown(self.body, safe_mode='escape'))
            #self.body_html = markdown(self.body, 'safe')
        elif self.markup == 'none':
            self.body_html = self.body
        else:
            raise Exception('Invalid markup property: %s' % self.markup)
        #self.body_text = strip_tags(self.body_html)
        self.body_html = urlize(self.body_html)
        if ydata_settings.SMILES_SUPPORT:
            self.body_html = smiles(self.body_html)
        super(Post, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self_id = self.id
        head_post_id = self.topic.posts.order_by('created')[0].id
        catalog = self.topic.catalog
        topic = self.topic
        self.last_topic_post.clear()
        self.last_catalog_post.clear()
        super(Post, self).delete(*args, **kwargs)
        #if post was last in topic - remove topic
        if self_id == head_post_id:
            topic.delete()
        else:
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

    def summary(self):
        LIMIT = 50
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
    reason = models.TextField('Reason', blank=True, default='', max_length='1000')

    class Meta:
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'

    def __unicode__(self):
        return u'%s %s' % (self.reported_by ,self.zapped)


# 附件
class Attachment(models.Model):
    post = models.ForeignKey(Post, verbose_name='Post', related_name='attachments')
    size = models.IntegerField('Size')
    content_type = models.CharField('Content type', max_length=255)
    path = models.CharField('Path', max_length=255)
    name = models.TextField('Name')
    hash = models.CharField('Hash', max_length=40, blank=True, default='', db_index=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Attachment, self).save(*args, **kwargs)
        if not self.hash:
            self.hash = sha_constructor(str(self.id) + settings.SECRET_KEY).hexdigest()
        super(Attachment, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('wiki:ydata_attachment', [self.hash])

    def get_absolute_path(self):
        return os.path.join(settings.MEDIA_ROOT, ydata_settings.ATTACHMENT_UPLOAD_TO,
                            self.path)

