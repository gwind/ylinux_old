#!/usr/bin/env python

import xmlrpclib
import traceback
import sys

# product URL
#YLINUX_XMLRPC="http://ylinux.org/xmlrpc/"
# devel URL
YLINUX_XMLRPC="http://127.0.0.1:8000/xmlrpc/"


class YLinuxClient(object):
    '''A Simple RPC client for YLinux'''

    def __init__(self, user, passwd, blogid=0, url=YLINUX_XMLRPC, verbose=False):
        self.server = xmlrpclib.ServerProxy(url, verbose=verbose)
        #self.server = xmlrpclib.ServerProxy(url, verbose=verbose, use_datetime=True)

        self.blogid = blogid
        self.user = user
        self.passwd = passwd

    def add_topic(self, struct, publish=True):

        try:
            return self.server.metaWeblog.newPost(self.blogid, self.user, self.passwd, struct, publish)
        except:
            traceback.print_exc()

    def edit_topic(self, postid, struct, publish=True):

        try:
            return self.server.metaWeblog.editPost(postid, self.user, self.passwd, struct, publish)
        except:
            traceback.print_exc()

    def delete_topic(self, id):

        try:
            return self.server.delete_topic(id, self.user, self.passwd)
        except:
            traceback.print_exc()

    def delete_all_topic(self):
        try:
            return self.server.delete_all_topic(self.user, self.passwd)
        except:
            traceback.print_exc()

    def list_recent_topics(self, numberOfPosts):

        topics = []
        try:
            topics = self.server.metaWeblog.getRecentPosts(self.blogid, self.user, 
                                                        self.passwd, numberOfPosts)
        except:
            traceback.print_exc()

        # print 
        for struct in topics:
            print struct

    def show_topic(self, postid):
        try:
            return self.server.metaWeblog.getPost(postid, self.user,self.passwd)
        except:
            traceback.print_exc()

    def show_category(self):
        try:
            return self.server.metaWeblog.getCategories(self.blogid, self.user,self.passwd)
        except:
            traceback.print_exc()

    def test(self):
        print self.server.system.listMethods()

if __name__ == "__main__":


    client = YLinuxClient('ray', 'ray')
    client.list_recent_topics(10)

    # choose one category
    categories = client.show_category()
    if len(categories) == 0:
        print "Not any category found, add some first"
        sys.exit()
    ca = categories[0]['categoryName']

    # add one topic, Need to add a catelog first! FIXME!!!
    topic = {'title':"a title", 'author':"chenran@163.com", 'category':ca,
                'description':"====This ia text from ylinux-client\n *one\n *two "}

    id = client.add_topic(topic)
    print client.show_topic(id)

    topic = {'title':'update title', 'description':'updated body'}
    if client.edit_topic(id, topic):
        print "Edit topic successfully"
        print client.show_topic(id)

    #if client.delete_topic(id):
    #    print "delete topic successfully"

    print "===== List all Topics ====="
    client.list_recent_topics(10)
