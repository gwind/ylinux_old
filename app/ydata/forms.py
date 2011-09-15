# coding: utf-8
import os, datetime

from django.conf import settings
from django import forms

from ydata.models import Topic, Post, Reputation, Report, Attachment, TZ_CHOICES, PRIVACY_CHOICES
from ydata import settings as ydata_settings
 

class AddPostForm(forms.ModelForm):
    name = forms.CharField(label='标题', max_length=256,
           widget=forms.TextInput)
    attachment = forms.FileField(label='附件', 
                                 required=False)

    class Meta:
        model = Post
        fields = ['body']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.topic = kwargs.pop('topic', None)
        self.ip = kwargs.pop('ip', None)
        super(AddPostForm, self).__init__(*args, **kwargs)

        if self.topic:
            self.fields['name'].widget = forms.HiddenInput()
            self.fields['name'].required = False

        self.fields['body'].widget = forms.Textarea(attrs={'class':'bbcode', 'rows':'10', 'cols':'60'})

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
        post = Post(topic=self.topic, user=self.user, user_ip=self.ip, markup='none', body=self.cleaned_data['body'])
        self.topic.post_count += 1
        self.topic.save()
        self.topic.catalog.post_count += 1
        self.topic.catalog.save()
        post.updated = datetime.datetime.now();
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


class AddTopicForm(forms.ModelForm):

    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Topic
        fields = ['catalog','name','markup']

    def __init__(self, *args, **kwargs):
        self.catalog = kwargs.pop('catalog', None)
        self.user = kwargs.pop('user', None)
        self.user_ip = kwargs.pop('user_ip', None)
        super(AddTopicForm, self).__init__(*args, **kwargs)

        self.fields['catalog'].initial = self.catalog.id
        if self.catalog:
            self.fields['catalog'].widget = forms.HiddenInput()

    def save(self):
        topic = Topic(name=self.cleaned_data['name'],
                user_ip=self.user_ip,
                markup=self.cleaned_data['markup'])
        topic.catalog=self.catalog
        topic.user=self.user
        topic.updated = datetime.datetime.now()
        topic.save()
        self.catalog.topic_count += 1
        self.catalog.save()
        text = self.cleaned_data['text'].encode('utf8')
        topic.save_file(text)
        return topic

class EditTopicForm(forms.ModelForm):

    text = forms.CharField(widget=forms.Textarea(
        attrs={'class':'markdown', 'rows':'20', 'cols':'65'}))


    class Meta:
        model = Topic
        fields = ['catalog','name','markup']

    def __init__(self, *args, **kwargs):
        self.old_text = kwargs.pop('text', None)
        self.user_ip = kwargs.pop('user_ip', None)
        super(EditTopicForm, self).__init__(*args, **kwargs)
        
        self.fields['text'].initial = self.old_text

    def save(self):
        topic = super(EditTopicForm, self).save(commit=False)
        topic.name = self.cleaned_data['name']
        topic.user_ip = self.user_ip
        topic.markup = self.cleaned_data['markup']
        topic.catalog=self.cleaned_data['catalog']
        topic.updated = datetime.datetime.now()
        topic.save()
        text = self.cleaned_data['text'].encode('utf8')
        topic.save_file(text)
        return topic
