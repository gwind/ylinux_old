#!/usr/bin/env python

import xmlrpclib
from xmlrpclib import Fault
import traceback
import sys,os

from optparse import OptionParser

# You can set YLINUX_XMLRPC env to specify what the Ylinux XMLRPC URL.
# That is: export YLINUX_XMLRPC="http://example.com/xmlprc/"

# product URL
YLINUX_XMLRPC = os.environ.get('YLINUX_XMLRPC', "http://ylinux.org/xmlrpc/")
# devel URL
#YLINUX_XMLRPC = os.environ.get('YLINUX_XMLRPC', "http://127.0.0.1:8000/xmlrpc/")

def u(s, encoding):
    '''convert string to unicode'''
    if isinstance(s, unicode):
        return s
    else:
        return unicode(s, encoding)

class YLinuxClient(object):
    '''A Simple XML-RPC client for YLinux'''

    def __init__(self, user, passwd, blogid=0, url=YLINUX_XMLRPC, verbose=False):
        self.server = xmlrpclib.ServerProxy(url, verbose=verbose)
        #self.server = xmlrpclib.ServerProxy(url, verbose=verbose, use_datetime=True)

        self.blogid = blogid
        self.user = user
        self.passwd = passwd

    def add_topic(self, struct, publish=True):

        try:
            return self.server.metaWeblog.newPost(self.blogid, self.user, self.passwd, struct, publish)
        except Fault, f:
            #traceback.print_exc()
            print str(f)
            return False

    def edit_topic(self, postid, struct, publish=True):

        try:
            return self.server.metaWeblog.editPost(postid, self.user, self.passwd, struct, publish)
        except Fault, f:
            #traceback.print_exc()
            print str(f)
            return False

    def delete_topic(self, id):

        try:
            return self.server.delete_topic(id, self.user, self.passwd)
        except Fault, f:
            #traceback.print_exc()
            print str(f)
            return False

    def delete_all_topic(self):
        try:
            return self.server.delete_all_topic(self.user, self.passwd)
        except Fault, f:
            #traceback.print_exc()
            print str(f)
            return False

    def list_recent_topics(self, numberOfPosts):

        topics = []
        try:
            topics = self.server.metaWeblog.getRecentPosts(self.blogid, self.user, 
                                                        self.passwd, numberOfPosts)
        except Fault, f:
            #traceback.print_exc()
            print str(f)
            return []

        # print 
        for struct in topics:
            print "="*80
            for key in struct.keys():
                print "%s : %s" %(key, struct[key])

    def show_topic(self, postid):
        try:
            return self.server.metaWeblog.getPost(postid, self.user,self.passwd)
        except Fault, f:
            print str(f)
            return None

        return True

    def show_category(self):
        categories = []
        try:
            categories =  self.server.metaWeblog.getCategories(self.blogid, self.user,self.passwd)
        except Fault, f:
            print str(f)
            return []

        # print
        for ca in categories:
            print "="*80
            for key in ca.keys():
                print "%s : %s" %(key, ca[key])

    def test(self):
        print self.server.system.listMethods()


def option_parser():

    usage="""
    A simple Ylinux Client.

    %s [-a][-d][-e][-l][-s][options] 

    List of commands:

    -a add     add one topic
    -l list    list recent topics
    -e edit    edit one topic
    -s show    show all category
    -d topci   delete one topic""" %sys.argv[0]

    parser = OptionParser(usage=usage)

    # Only add/delete/edit/list operations are supported
    parser.add_option("-a", "--add", action="store_const", const=1, dest="mode",help="add one topic")
    parser.add_option("-d", "--delete", action="store_const", const=2, dest="mode",help="delete one topic")
    parser.add_option("-e", "--edit", action="store_const", const=3, dest="mode",help="edit one topic")
    parser.add_option("-l", "--list", action="store_const", const=4, dest="mode",help="list recent topic")
    parser.add_option("-s", "--show", action="store_const", const=5, dest="mode",help="show all category")

    parser.add_option("-u", "--user", dest="user", help="specify user account")
    parser.add_option("-p", "--passwd", dest="passwd", help="specify account passwd")
    parser.add_option("-t", "--title", default="No Title", help="topic title, default is 'No Title'")
    parser.add_option("-c", "--category", help="specify which category to write")
    parser.add_option("-i", "--id", help="specify which topic id")
    parser.add_option("-m", "--body", help="topic body text. support 'markdown'")
    parser.add_option("-f", "--file", dest="filename", help="Load topic body from file ")
    parser.add_option("-n", "--number", default=5, type="int",dest="count", 
                        help="specify how many counts to list, default is 5")

    return parser.parse_args()

def main():

    (options, args) = option_parser()
    #print options, args

    if not options.user:
        print "[-u] Ylinux user account is required!"
        sys.exit()
    else:
        if not options.passwd:
            print "[-p] user password is required!"
            sys.exit()

    # init a client
    c = YLinuxClient(options.user, options.passwd)

    # add topic
    if options.mode == 1:

        # get topic text first
        text = ""
        if options.body:
            if options.filename:
                print "[-m] or [-f] option is excluded!"
                sys.exit()
            else:
                text = options.body
        else:
            if options.filename:
                with open(options.filename, 'r') as f:
                    text = f.read()
            else:
                print "[-m] or [-f] option is required for topic text!"
                sys.exit()

        # specify which category
        if not options.category:
            print "[-c] option is required for topic category!"
            sys.exit()

        topic = {'title':u(options.title, 'utf8'), 'category':u(options.category, 'utf8'),
                'description':u(text, 'utf8')}
        id = c.add_topic(topic)
        if id:
            print "add topic successfully!"
            print "Try this command for topic detail."
            print "  ylinux-client -u %s -p %s -l -i %d" %(options.user, options.passwd, id)
            print "or web visit -> /topic/%d" %id

    elif options.mode == 2:
        # delte topic
        if not options.id:
            print "[-i] topic id is required for delete topic!"
            sys.exit()

        if c.delete_topic(options.id):
            print "delete topic successfully!"

    elif options.mode == 3:
        # edit topic
        if not options.id:
            print "[-i] topic id is required for edit topic!"
            sys.exit()

        # get topic text first
        text = ""
        if options.body:
            if options.filename:
                print "[-m] or [-f] option is excluded!"
                sys.exit()
            else:
                text = options.body
        else:
            if options.filename:
                with open(options.filename, 'r') as f:
                    text = f.read()
            else:
                print "[-m] or [-f] option is required for topic text!"
                sys.exit()

        topic = {}
        # if title is not input, don't modify title
        if not options.title == "No Title":
            topic = {'title':u(options.title, 'utf8'), 'description':u(text, 'utf8')}
        else:
            topic = {'description':u(text, 'utf8')}
        if c.edit_topic(options.id, topic):
            print "edit topic successfully!"

    elif options.mode == 4:
        # list topic
        if options.id:
            struct = c.show_topic(options.id)
            if not struct:
                print "list topic failed!"
                sys.exit()

            print "="*80
            for key in struct.keys():
                print "%s : %s" %(key, struct[key])
        else:
            c.list_recent_topics(options.count)
    elif options.mode == 5:
        # show category
        c.show_category()

    else:
        print "Please input Support operation: [-a][-d][-e][-l][-s]"
        sys.exit()
    
    # end
    
def test():

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

if __name__ == "__main__":

    #test()
    main()
