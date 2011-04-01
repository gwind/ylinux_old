# coding: utf-8

from HTMLParser import HTMLParser
import re

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import urlize as django_urlize

from ydata import settings as ydata_settings

_SMILES = [(re.compile(smile_re), path) for smile_re, path in ydata_settings.SMILES]



def render_to(template):

    def renderer(function):
        def wrapper(request, *args, **kwargs):
            output = function(request, *args, **kwargs)
            if not isinstance(output, dict):
                return output
            tmpl = output.pop('TEMPLATE', template)
            return render_to_response(tmpl, output, context_instance=RequestContext(request))
        return wrapper
    return renderer


class ExcludeTagsHTMLParser(HTMLParser):
        """ 
        Class for html parsing with excluding specified tags.
        """

        def __init__(self, func, tags=('a', 'code')):
            HTMLParser.__init__(self)
            self.func = func
            self.is_ignored = False
            self.tags = tags
            self.html = []

        def handle_starttag(self, tag, attrs):
            self.html.append('<%s%s>' % (tag, self.__html_attrs(attrs)))
            if tag in self.tags:
                self.is_ignored = True

        def handle_data(self, data):
            if not self.is_ignored:
                data = self.func(data)
            self.html.append(data)

        def handle_startendtag(self, tag, attrs):
            self.html.append('<%s%s/>' % (tag, self.__html_attrs(attrs))) 

        def handle_endtag(self, tag):
            self.is_ignored = False
            self.html.append('</%s>' % (tag))

        def handle_entityref(self, name):
            self.html.append('&%s;' % name)

        def handle_charref(self, name):
            self.html.append('&#%s;' % name)

        def unescape(self, s):                                                                                              
            #we don't need unescape data (without this possible XSS-attack)                                                 
            return s

        def __html_attrs(self, attrs):
            _attrs = ''
            if attrs:
                _attrs = ' %s' % (' '.join([('%s="%s"' % (k,v)) for k,v in attrs]))
            return _attrs

        def feed(self, data):
            HTMLParser.feed(self, data)
            self.html = ''.join(self.html)


def urlize(data):
    """ 
    Urlize plain text links in the HTML contents.
   
    Do not urlize content of A and CODE tags.
    """

    parser = ExcludeTagsHTMLParser(django_urlize)
    parser.feed(data)
    urlized_html = parser.html
    parser.close()
    return urlized_html


def _smile_replacer(data):
    for smile, path in _SMILES:
        data = smile.sub(path, data)
    return data

def smiles(data):
    """ 
    Replace text smiles.
    """

    parser = ExcludeTagsHTMLParser(_smile_replacer)
    parser.feed(data)
    smiled_html = parser.html
    parser.close()
    return smiled_html


def build_form(Form, _request, GET=False, *args, **kwargs):
    """ 
    Shorcut for building the form instance of given form class
    """

    if not GET and 'POST' == _request.method:
        form = Form(_request.POST, _request.FILES, *args, **kwargs)
    elif GET and 'GET' == _request.method:
        form = Form(_request.GET, _request.FILES, *args, **kwargs)
    else:
        form = Form(*args, **kwargs)
    return form


def old_get_parents(model,parent):
    ''' 方便导航，得到一系列父目录/项目的（id，name）list
    
    输入： model = Catalog/Project , parent=(catalog/project).parent
    输出： parents 类似 [(1,'First'),(2,'Second'),(3,'Third')]
    '''
    parents = []
    while parent:
        t = parent.id,parent.name
        parents.append(t)
        try:
            parent = model.objects.get(pk=parent.parent.id)
        except parent.DoesNotExist:
            parent = None
        except  AttributeError:
            parent = None

    # list 的 reverse 方法直接作用，返回 None！
    parents.reverse()
    return parents


def get_parents(m, id):
    ''' Model 的 parent '''
    parent = m.objects.get (pk=id)
    parents = []
    while parent:
        t = parent.id,parent.name
        parents.append(t)
        try:
            parent = m.objects.get(pk=parent.parent.id)
        except parent.DoesNotExist:
            parent = None
        except  AttributeError:
            parent = None

    # list 的 reverse 方法直接作用，返回 None！
    parents.reverse()
    return parents

def ylinux_get_ip(request):
    ''' 从 request 里获得用户的 ip  '''

    #ip = request.META.get('REMOTE_ADDR', None)
    try:
        real_ip = request.META['HTTP_X_FORWARDED_FOR']
    except KeyError:
        ip = request.META.get('REMOTE_ADDR', None)
    else:
        ip = real_ip.split(",")[0].strip()

    return ip

