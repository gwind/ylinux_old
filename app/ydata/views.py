# coding: utf-8

from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
#from django.contrib.syndication.views import Feed
from syndication.views import Feed

from account.decorators import login_required, permission_required
from ydata.models import Catalog,Topic,Post,Attachment
from ydata.forms import AddPostForm, \
    AddTopicForm, EditTopicForm

from ydata.util import render_to, build_form, get_parents, ylinux_get_ip

from django.conf import settings
from ydata import settings as ydata_settings
import os, hashlib, mimetypes, urllib

from string import Template

# dic = {'ID':XXX, 'URL':XXX, 'THUMBNAIL':XXX, 'DURL':XXX}
attachment_response_innerHTML = Template(u'<tr>\
<td>$ID</td>\
<td><a href="$URL">$NAME</a></td>\
<td>$THUMBNAIL</td>\
<td><a href="$DURL">$DURL</a></td>\
</tr>')


@login_required
def upload_single_file(req, id):
    ''' 上传单个附件， 只作异步上传使用
    1. 上传的 form 中文件的 name = 'single_file'
    '''

    if req.method != 'POST':
        return HttpResponse("Just for POST a single file")

    f = req.FILES['single_file'] #req.FILES.values()[0]
    if f.size > ydata_settings.ATTACHMENT_SIZE_LIMIT:
        notes = u'文件太大： %s (限制大小： %s)' % (f.size, ydata_settings.ATTACHMENT_SIZE_LIMIT)
        r = u'<script type="text/javascript">window.parent.UploadError("%s");</script>' % notes
        return HttpResponse(r)

    #topic = get_object_or_404(Topic, pk=id)
    try:
        topic = Topic.objects.get(pk=id)
    except Topic.DoesNotExist:
        topic = False

    sha1_hash = hashlib.sha1()
    for chunk in f.chunks():
        sha1_hash.update(chunk)
    fhash = sha1_hash.hexdigest()

    attachments = Attachment.objects.filter(hash=fhash)
    notes = ''

    if attachments:
        # 此文件在服务器上已存在， 增加引用计数即可
        local_name = ''
        attachment = False
        for a in attachments:
            if local_name == '':
                local_name = a.path
            if a.user == req.user:
                attachment = a
                notes = u'文件已经存在，请不要重复上传。'
            a.qtimes += 1
            a.save()
        if not attachment:
            attachment = Attachment(user=req.user, name=f.name, path=local_name, size=f.size, hash=fhash, qtimes=2)
            if topic:
                attachment.topic = topic

    else:
        local_name = str(id) + '-' + str(req.user.id) + '-' + f.name
        save_path = os.path.join(settings.MEDIA_ROOT,
                                 ydata_settings.ATTACHMENT_UPLOAD_TO,
                                 local_name)
        save_file = open(save_path, 'wb+')
        for chunk in f.chunks():
            save_file.write(chunk)

        attachment = Attachment(user=req.user, name=f.name, path=local_name, size=f.size, hash=fhash)
        if topic:
            attachment.topic = topic

    attachment.save()
    r = u'<script type="text/javascript">window.parent.AfterSubmit("%s","%s","%s","%s","%s");</script>'\
        % (attachment.id, attachment.name,
           reverse ('ydata:show_attachment', args=[attachment.id]),
           reverse ('ydata:download_attachment', args=[attachment.id]),
           notes)

    print r
    return HttpResponse(r)


@render_to('ydata/attachment.html')
def show_attachment(req, id):
    ''' 显示指定 id 的附件信息 '''
    attachment = get_object_or_404(Attachment,pk=id)    
    return {'attachment': attachment}



@login_required
@render_to('ydata/attachment.html')
def remove_attachment(req, id):
    ''' 删除指定 id 的附件信息 '''
    a = get_object_or_404(Attachment,pk=id)
    return {'attachment': a}


def download_attachment(request, id):

    a = get_object_or_404(Attachment,pk=id)

    a.dtimes += 1
    a.save()

    print a.get_absolute_path()
    f = open(a.get_absolute_path())
    response = HttpResponse(f.read())
    f.close()

    type, encoding = mimetypes.guess_type(a.get_absolute_path())
    if type is None:
        type = 'application/octet-stream'
    response['Content-Type'] = type
    response['Content-Length'] = str(a.size)
    if encoding is not None:
        response['Content-Encoding'] = encoding

    # To inspect details for the below code, see http://greenbytes.de/tech/tc2231/
    if u'WebKit' in request.META['HTTP_USER_AGENT']:
        # Safari 3.0 and Chrome 2.0 accepts UTF-8 encoded string directly.
        filename_header = 'filename=%s' % a.name.encode('utf-8')
    elif u'MSIE' in request.META['HTTP_USER_AGENT']:
        # IE does not support internationalized filename at all.
        # It can only recognize internationalized URL, so we do the trick via routing rules.
        filename_header = ''
    else:
        # For others like Firefox, we follow RFC2231 (encoding extension in HTTP headers).
        filename_header = 'filename*=UTF-8\'\'%s' % urllib.quote(a.name.encode('utf-8'))
    response['Content-Disposition'] = 'attachment; ' + filename_header
    return response
