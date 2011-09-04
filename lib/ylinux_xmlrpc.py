# coding: utf-8
#

"""
 XML-RPC public interface for YLinux

"""

import sys,os
from datetime import datetime
from time import strftime, mktime,strptime
from xmlrpclib import Fault, Boolean, DateTime

from account import authenticate,login
from ydata.models import Topic,Catalog,User

def datetime_from_iso(isostring):

    try:
        isostring = isostring.split(".")[0]
    except:
        pass
    
    ret = isostring
    try:
        ret = datetime.fromtimestamp(mktime(strftime(isostring, '%Y%m%dT%H:%M:%SZ')))
    except:
        ret = datetime.fromtimestamp(mktime(strftime(isostring, '%Y%m%dT%H:%M:%S')))

    return ret

def has_auth(user, passwd):

    user = authenticate(username=user, password=passwd)
    if user is not None:
        return True
    else:
        return False

def delete_topic(id, user, passwd):
    '''delete one topic'''
    if not has_auth(user, passwd):
        raise Fault(-1, "Authentication Failure")

    try:
        topic = Topic.objects.get(pk=id)
        topic.posts.all().delete()
        topic.delete()
        return True
    except:
        raise Fault(-1, "delete one topic failed")

def delete_all_topic(user, passwd):
    '''delete all topic'''
    if not has_auth(user, passwd):
        raise Fault(-1, "Authentication Failure")

    try:
        Topic.objects.all().delete()
        return True
    except:
        raise Fault(-1, "delete all topics failed")

###
### MetaWeblog API
###
def topic_to_struct(topic):

    return { 'userid' : topic.user.id,
             'pubDate' : topic.updated.isoformat(),
             'dateCreated' : topic.created.isoformat(),
             'postid' : str(topic.id),
             'description' : topic.body,
             'title' : topic.name,
             'category' : topic.catalog.name,
             'link' : topic.get_absolute_url(),
             'permalink' : topic.get_absolute_url(),
            }

#   Category struct
#
#    ‘categoryID’ – ID of the category
#    ‘parentID’ – ID of the category’s parent
#    ‘description’ – Name of the category
#    ‘categoryDescription’ – Description of the category
#    ‘categoryName’ – Name of the category
#    ‘htmlUrl’ – Category permalink
#    ‘rssUrl’ – RSS feed for the category
def category_to_struct(cate):
    return {'description':cate.description,
            'summary':cate.summary,
            'categoryName':cate.name,
            'htmlUrl':cate.get_absolute_url(),
            'categoryID': 1, # TODO:FIXME!!
            'parentID':1,
            }

def new_media(blogid, user, passwd, fileObject):
    '''upload media or acctachment
    
       struct = {'name':, 'type':, 'bits'}
    '''
    if not has_auth(user, passwd):
        raise Fault(-1, "Authentication Failure")

    file_data = str(fileObject['bits'])
    file_name = fileObject['name'].encode('utf8')
    file_type = 'img'
    
    # TODO: figure out saving files api in django
    
    if file_type == 'img':
        dated_path = datetime.now().strftime('%Y_%m_%d_') + os.path.basename(file_name)
        relative_path = os.path.join(file_type, dated_path)
        target_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        target_url = '%s/%s' % (settings.MEDIA_URL, relative_path)
        open(target_path, 'w').write(file_data)
        return {'url': target_url}
    
    return ''

def get_topic(postid, user, passwd):
    '''return a topic'''

    if not has_auth(user, passwd):
        raise Fault(-1, "Authentication Failure")

    try:
        topic = Topic.objects.get(pk = int(postid))
        return topic_to_struct(topic)
    except Topic.DoesNotExist:
        raise Fault(-2, "Topic does not exist")
    except Exception, e:
        raise Fault(-255, 'Unknown Exception: %s' % str(e))

def get_recent_topics(postid, user, passwd, count):
    '''get recent topics'''

    if not has_auth(user,passwd):
        raise Fault(-1, "Authentication Failure")

    topics = Topic.objects.order_by('-updated')[:count]
    try:
        return [topic_to_struct(t) for t in topics]
    except Exception, e:
        raise Fault(-255, 'Unknown Exception: %s' % str(e))
        
def get_categories(blogid, user, passwd):
    '''show all category'''
    
    if not has_auth(user, passwd):
        raise Fault(-1, "Authentication Failure")

    cate = Catalog.objects.all()
    try:
        return [category_to_struct(c) for c in cate]
    except Exception, e:
        raise Fault(-255, 'Unknown Exception: %s' % str(e))
        

def edit_topic(postid, user, passwd, struct, publish):
    '''Edit one topic'''
    if not has_auth(user, passwd):
        raise Fault(-1, "Authentication Failure")

    try:
        topic = Topic.objects.get(pk=postid)
        if struct.has_key('title'):
            topic.name = struct['title']

        topic.save()
        if struct.has_key('description'):
            topic.save_file(struct['description'])

        return True
    except Exception, e:
        raise Fault(-255, "Failed to edit topic: %s" %str(e))

def new_topic(blogid, user, passwd, struct, publish):
    '''Add one topic'''

    if not has_auth(user, passwd):
        raise Fault(-1, "Authentication Failure")

    title = struct.get('title', "No Topic")
    markup = struct.get('markup', "markdown")

    topic = Topic(name=title, markup=markup)
    topic.updated = datetime.now()

    catalog = Catalog.objects.get(name=struct['category'])
    topic.catalog = catalog

    # find which user
    topic.user = User.objects.get(username=user)
    topic.save()
    catalog.last_topic = topic
    catalog.topic_count += 1
    catalog.save()

    text = struct.get('description', "")
    topic.save_file(text)
    return topic.id

###
### Blogger API
###

def blogger_getUsersBlogs(appkey, username, password):
    if not auth_user(username, password):
        raise Fault(-1, "Authentication Failure")
    site = Site.objects.get_current()
    return [{'url': 'http://%s/' % site.domain,
             'blogid': BLOG_ID,
             'blogName': site.name},]

def blogger_getUserInfo(appkey, username, password):
    if not auth_user(username, password):
        raise Fault(-1, "Authentication Failure")

    site = Site.objects.get_current()
    user = User.objects.get(username = username)
    return {'url': 'http://%s/' % site.domain,
            'nickname': user.username,
            'userid': '1',
            'email': user.email,
            'lastname': user.last_name,
            'firstname': user.first_name,}

def blogger_deletePost(appkey, postid, username, password, publish):
    if not auth_user(username, password):
        raise Fault(-1, "Authentication Failure")
    
    try:
        b = BlogEntry.objects.get(pk = postid)
        b.published = False
        b.save()
        return Boolean(True)
    except BlogEntry.DoesNotExist:
        raise Fault(-2, "Post does not exist")
    except Exception, e:
        raise Fault(-255, "Failed to create new post: %s" % str(e))

