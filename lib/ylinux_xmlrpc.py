# coding: utf-8
#

"""
 XML-RPC public interface for YLinux

"""

import sys
import datetime

from ydata.models import Topic,Catalog,User

XMLRPC_METHODS = (
    ('ylinux_xmlrpc.list_all_topic', 'list_all_topic'),
    ('ylinux_xmlrpc.show_topic', 'show_topic'),
    ('ylinux_xmlrpc.add_topic', 'add_topic'),
    ('ylinux_xmlrpc.edit_topic', 'edit_topic'),
    ('ylinux_xmlrpc.delete_topic', 'delete_topic'),
    ('ylinux_xmlrpc.delete_all_topic', 'delete_all_topic'),
)


def list_all_topic():
    '''list all topic'''
    topics = Topic.objects.all()
    return "\n".join(map(lambda x: x.body, topics))


def show_topic(id):
    '''show one topic [id]'''

    try:
        topic = Topic.objects.get(pk=id)
    except:
        print "No [%d] topic found" %id
        
    return topic.body


def edit_topic(id):
    pass


def delete_topic(id):
    '''delete one topic'''
    topic = Topic.objects.get(pk=id)
    topic.posts.all().delete()
    return topic.delete()

def delete_all_topic():
    '''delete one topic'''
    return Topic.objects.all().delete()

def add_topic(title, text, user, cata_id):
    '''Add one topic'''

    if not cata_id:
        print "No [%d] catalog found" %cata_id
        return 

    catalog = Catalog.objects.get(pk=cata_id)
    topic = Topic(name=title, markup="markdown")
    topic.catalog = catalog
    topic.updated = datetime.datetime.now()

    # find which user
    topic.user = User.objects.get(username=user)
    topic.save()
    catalog.last_topic = topic
    catalog.topic_count += 1
    catalog.save()

    topic.save_file(text)
