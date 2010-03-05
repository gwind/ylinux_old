# coding: utf-8

from django import forms

from ydata.models import Topic, Post, Reputation, Report, Attachment, TZ_CHOICES, PRIVACY_CHOICES
from ydata import settings as ydata_settings
 

#class AddPostForm(forms.ModelForm):
#    name = forms.CharField(label='Subject', max_length=255,
#                           widget=forms.TextInput(attrs={'size':'115'}))
#
#    class Meta:
#        model = Post

# 发表 Post
class AddPostForm(forms.ModelForm):
    name = forms.CharField(label='Subject', max_length=255,
                           widget=forms.TextInput(attrs={'size':'115'}))
    attachment = forms.FileField(label='Attachment', required=False)

    class Meta:
        model = Post
        fields = ['body']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.topic = kwargs.pop('topic', None)
        self.catalog = kwargs.pop('catalog', None)
        self.ip = kwargs.pop('ip', None)
        super(AddPostForm, self).__init__(*args, **kwargs)

        if self.topic:
            self.fields['name'].widget = forms.HiddenInput()
            self.fields['name'].required = False

        self.fields['body'].widget = forms.Textarea(attrs={'class':'bbcode', 'rows':'20', 'cols':'95'})

        if not ydata_settings.ATTACHMENT_SUPPORT:
            self.fields['attachment'].widget = forms.HiddenInput()
            self.fields['attachment'].required = False

    def clean_attachment(self):
        if self.cleaned_data['attachment']:
            memfile = self.cleaned_data['attachment']
            if memfile.size > ydata_settings.ATTACHMENT_SIZE_LIMIT:
                raise forms.ValidationError('Attachment is too big')
            return self.cleaned_data['attachment']


    def save(self):
        if self.catalog:
            topic = Topic(catalog=self.catalog,
                          user=self.user,
                          name=self.cleaned_data['name'])
            topic.save()
        else:
            topic = self.topic

        post = Post(topic=topic, user=self.user, user_ip=self.ip,
                    markup='none',
                    body=self.cleaned_data['body'])

        post.save()
        if ydata_settings.ATTACHMENT_SUPPORT:
            self.save_attachment(post, self.cleaned_data['attachment'])
        return post


    def save_attachment(self, post, memfile):
        if memfile:
            obj = Attachment(size=memfile.size, content_type=memfile.content_type,
                             name=memfile.name, post=post)
            dir = os.path.join(settings.MEDIA_ROOT, ydata_settings.ATTACHMENT_UPLOAD_TO)
            fname = '%d.0' % post.id
            path = os.path.join(dir, fname)
            file(path, 'w').write(memfile.read())
            obj.path = fname
            obj.save()

