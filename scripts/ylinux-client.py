#!/usr/bin/env python

import xmlrpclib

# product URL
#YLINUX_XMLRPC="http://ylinux.org/xmlrpc/"
# devel URL
YLINUX_XMLRPC="http://127.0.0.1:8000/xmlrpc/"


class User(object):
    def __init__(self, name):
        self.name = name

    def id(self):

        pass

class Catalog(object):
    def __init__(self,name):
        self.name = name

class Topic(object):

    def __init__(self, title=None, text="", catalog=None, user=None):

        self.title = title
        if not title:
            self.tilte = "No Topics"
        self.text = text
        self.catalog = catalog
        self.user = user
    
class YLinuxClient(object):
    '''A Simple RPC client for YLinux'''

    def __init__(self, url=YLINUX_XMLRPC, verbose=False):
        self.server = xmlrpclib.ServerProxy(url, verbose=verbose)


    def add_topic(self, topic):

        title = topic.title
        text = topic.text
        user = topic.user
        catalog = topic.catalog
        try:
            self.server.add_topic(title, text, user, catalog)
        except:
            pass


    def delete_topic(self, id):

        self.server.delete_topic(id)        

    def delete_all_topic(self):
        try:
            self.server.delete_all_topic()      
        except:
            pass  

    def list_all_topic(self):
        try:
            ret = self.server.list_all_topic()
        except:
            pass

        return ret

    def show_topic(self, id):
        return self.server.show_topic(id)

    def test(self):
        print self.server.system.listMethods()

if __name__ == "__main__":


    client = YLinuxClient()
    #client.delete_all_topic()

    # add one topic, Need to add a catelog first! FIXME!!!
    topic = Topic(title="a title", user='ray', catalog=1,
                text="====This ia text from ylinux-client\n *one\n *two ")

    client.add_topic(topic)
    #print client.show_topic(1)
    print client.list_all_topic()
