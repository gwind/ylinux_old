# coding: utf-8
import datetime

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.db.models.manager import EmptyManager
from django.utils.encoding import smart_str
from django.utils.hashcompat import md5_constructor, sha_constructor


UNUSABLE_PASSWORD = '!' # This will never be a valid hash


# 设置密码
def get_hexdigest(algorithm, salt, raw_password):
    """根据 algorithm,salt,raw_password 参数返回加密后的密码字符串。
    支持 'md5', 'sha1' 和 'crypt' 三种加密算法。
    """
    raw_password, salt = smart_str(raw_password), smart_str(salt)
    if algorithm == 'crypt':
        try:
            import crypt
        except ImportError:
            raise ValueError('当前环境不支持 "crypt" 加密算法！')
        return crypt.crypt(raw_password, salt)

    if algorithm == 'md5':
        return md5_constructor(salt + raw_password).hexdigest()
    elif algorithm == 'sha1':
        return sha_constructor(salt + raw_password).hexdigest()
    raise ValueError("未知加密算法")


# 检查密码
def check_password(raw_password, enc_password):
    """
    Returns a boolean of whether the raw_password was correct. Handles
    encryption formats behind the scenes.
    """
    algo, salt, hsh = enc_password.split('$')
    return hsh == get_hexdigest(algo, salt, raw_password)


# 由于 Permission, Group, User 之间的相互关系，
# 按照 Permission->Group->User 顺序定义方便传递对象而非名字

class Permission(models.Model):
    """权限"""
    
    name = models.CharField('权限名', max_length=50)
    content_type = models.ForeignKey(ContentType,
                        related_name="permission_content_type")
    codename = models.CharField('codename', max_length=100)

    class Meta:
        verbose_name = '权限'
        verbose_name_plural = '权限'
        unique_together = (('content_type', 'codename'),)
        ordering = ('content_type__app_label', 'codename')

    def __unicode__(self):
        return u"%s | %s | %s" % (
            unicode(self.content_type.app_label),
            unicode(self.content_type),
            unicode(self.name))

class Group(models.Model):
    """组可以简单分配权限"""
    
    name = models.CharField("组名", max_length=80, unique=True)
    permissions = models.ManyToManyField(Permission,
                        verbose_name='权限', blank=True)

    class Meta:
        verbose_name = '组'
        verbose_name_plural = '组'

    def __unicode__(self):
        return self.name


class UserManager(models.Manager):
    def create_user(self, username, email, password=None):
        "Creates and saves a User with the given username, e-mail and password."
        now = datetime.datetime.now()
        #user = self.model(None, username, '', '', email.strip().lower(), 'placeholder', False, True, False, now, now)
        user = self.model(username=username, email=email.strip().lower(),
                          date_joined=now, last_login=now)        
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def create_superuser(self, username, email, password):
        u = self.create_user(username, email, password)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save()
        return u

    def make_random_password(self, length=10, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'):
        "Generates a random password with the given length and given allowed_chars"
        # Note that default value of allowed_chars does not have "I" or letters
        # that look like it -- just to avoid confusion.
        from random import choice
        return ''.join([choice(allowed_chars) for i in range(length)])


class User(models.Model):
    """用户模型，定义一个用户的基本信息。"""

    GENDER = (
        (0, '保密'),
        (1, '小姐'),
        (2, '公子'),
        )
    
    username = models.CharField("用户名",max_length=30,unique=True,
                help_text="不能与社区已有用户名重复，可更改！")
    first_name = models.CharField("名",max_length=15,blank=True)
    last_name = models.CharField("姓",max_length=15,blank=True)
    gender = models.IntegerField(default=0,choices=GENDER)

    # email 以后要唯一，暂且随意
    email = models.EmailField("Email",blank=True)
    password = models.CharField("密码",max_length=128,
                help_text="为了您的利益和社区的安全，请复杂点！")

    is_active = models.BooleanField("激活",default=True,
                help_text="这里决定此用户是否可用！")
    is_superuser = models.BooleanField("root",default=False)

    last_login = models.DateTimeField("最后登录",
                                    default=datetime.datetime.now)
    date_joined = models.DateTimeField("注册日期",
                                    default=datetime.datetime.now)
    groups = models.ManyToManyField(Group, verbose_name='所属组',
                blank=True,
                help_text="用户可以获得每个组的所有权限")
    user_permissions = models.ManyToManyField(Permission,
                verbose_name='用户权限', blank=True)
    objects = UserManager()
    
    class Meta:
        verbose_name = "用户"
        verbose_name_plural = '用户'

    def __unicode__(self):
        return self.username

    def get_absolute_url(self):
        return "/users/%s/" % urllib.quote(smart_str(self.username))

    def is_anonymous(self):
        "本类的对象都不是匿名用户"
        return False

    def is_authenticated(self):
        "一个通用的在模板里方便地判断用户是否经过认证的方法"
        return True

    def get_full_name(self):
        "中文一般连写，英文却要空格，留待后面实现"
        full_name = u'%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def set_password(self, raw_password):
        "设置密码"
        import random
        algo = 'sha1'
        salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
        hsh = get_hexdigest(algo, salt, raw_password)
        self.password = '%s$%s$%s' % (algo, salt, hsh)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        encryption formats behind the scenes.
        """
        # Backwards-compatibility check. Older passwords won't include the
        # algorithm or salt.
        if '$' not in self.password:
            is_correct = (self.password == get_hexdigest('md5', '', raw_password))
            if is_correct:
                # Convert the password to the new, more secure format.
                self.set_password(raw_password)
                self.save()
            return is_correct
        return check_password(raw_password, self.password)

    def set_unusable_password(self):
        # Sets a value that will never be a valid hash
        self.password = UNUSABLE_PASSWORD



# 匿名用户模型
class AnonymousUser(object):
    id = None
    username = ''
    is_staff = False
    is_active = False
    is_superuser = False
    _groups = EmptyManager()
    _user_permissions = EmptyManager()

    def __init__(self):
        pass

    def __unicode__(self):
        return 'AnonymousUser'

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return 1 # instances always return the same hash value

    def save(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def set_password(self, raw_password):
        raise NotImplementedError

    def check_password(self, raw_password):
        raise NotImplementedError

    def _get_groups(self):
        return self._groups
    groups = property(_get_groups)

    def _get_user_permissions(self):
        return self._user_permissions
    user_permissions = property(_get_user_permissions)

    def has_perm(self, perm):
        return False

    def has_perms(self, perm_list):
        return False

    def has_module_perms(self, module):
        return False

    def get_and_delete_messages(self):
        return []

    def is_anonymous(self):
        return True

    def is_authenticated(self):
        return False

