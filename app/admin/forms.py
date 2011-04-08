# coding: utf-8

from django import forms

from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from account.models import Permission,Group,User
from ydata.models import Catalog, Topic, Post, Reputation, Report, Attachment, TZ_CHOICES, PRIVACY_CHOICES
from ydata import settings as ydata_settings


class AddPermissionForm (forms.ModelForm):
    class Meta:
        model = Permission
        
    def __init__ (self, *args, **kwargs):
        super (AddPermissionForm, self).__init__ (*args, **kwargs)

    def save (self):
        permission = Permission (name=self.cleaned_data['name'], content_type=self.cleaned_data['content_type'], codename=self.cleaned_data['codename'])
        permission.save()
        return permission

class EditPermissionForm (forms.ModelForm):

    class Meta:
        model = Permission

    def __init__ (self, *args, **kwargs):
        super(EditPermissionForm, self).__init__(*args, **kwargs)

    def save (self):
        permission = super(EditPermissionForm, self).save(commit=False)
        permission.name = self.cleaned_data['name']
        permission.codename = self.cleaned_data['codename']
        permission.content_type = self.cleaned_data['content_type']
        permission.save()
        return permission


class AddGroupForm (forms.ModelForm):

    class Meta:
        model = Group

    def __init__ (self, *args, **kwargs):
        super(AddGroupForm, self).__init__(*args, **kwargs)

    def save (self):
        group = Group(name=self.cleaned_data['name'])
        group.save()
        for perm in self.cleaned_data['permissions']:
            group.permissions.add(perm)
        return group


class EditGroupForm (forms.ModelForm):

    class Meta:
        model = Group

    def __init__ (self, *args, **kwargs):
        super(EditGroupForm, self).__init__(*args, **kwargs)

    def save (self):
        group = super(EditGroupForm, self).save(commit=False)
        group.name = self.cleaned_data['name']
        group.save()
        for perm in self.cleaned_data['permissions']:
            group.permissions.add(perm)
        return group


class AddUserForm (forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions']

    def __init__ (self, *args, **kwargs):
        super(AddUserForm, self).__init__(*args, **kwargs)

    def save (self):
        user = User(username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                is_staff=self.cleaned_data['is_staff'],
                is_active=self.cleaned_data['is_active'],
                is_superuser=self.cleaned_data['is_superuser'],
                )
        user.save()
        for g in self.cleaned_data['groups']:
            user.groups.add(g)
        for p in self.cleaned_data['user_permissions']:
            user.user_permissions.add(p)
        return user


class EditUserForm (forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions']

    def __init__ (self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)

    def save (self):
        user = super(EditUserForm, self).save(commit=False)
        user.username=self.cleaned_data['username']
        user.email=self.cleaned_data['email']
        user.is_staff=self.cleaned_data['is_staff']
        user.is_active=self.cleaned_data['is_active']
        user.is_superuser=self.cleaned_data['is_superuser']
        user.set_password(self.cleaned_data['password'])
        user.save()
        for g in self.cleaned_data['groups']:
            user.groups.add(g)
        for p in self.cleaned_data['user_permissions']:
            user.user_permissions.add(p)
        return user


class AddCatalogForm(forms.ModelForm):

    class Meta:
        model = Catalog
        fields = ['name','parent', 'position','summary', 'description', 'groups']
        
    def __init__ (self, *args, **kwargs):
        self.parent = kwargs.pop('parent', None)
        super(AddCatalogForm, self).__init__(*args, **kwargs)

        if self.parent:
            self.fields['parent'].widget = forms.HiddenInput()

        self.fields['description'].widget = forms.Textarea()

    def save (self):
        catalog = Catalog(name=self.cleaned_data['name'],
                parent=self.parent,
                position=self.cleaned_data['position'],
                summary=self.cleaned_data['summary'],
                description=self.cleaned_data['description'],)
        catalog.save()
        for g in self.cleaned_data['groups']:
            catalog.groups.add(g)
        return catalog            


class EditCatalogForm(forms.ModelForm):

    class Meta:
        model = Catalog
        fields = ['name','parent', 'position','summary', 'description','groups']

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop('parent', None)
        super(EditCatalogForm, self).__init__(*args, **kwargs)
        self.fields['parent'].initial = self.parent
        self.fields['description'].widget = forms.Textarea()

    def save(self,commit=True):
        catalog = super(EditCatalogForm, self).save(commit=False)
        catalog.parent = self.cleaned_data['parent']
        catalog.name = self.cleaned_data['name']
        catalog.position = self.cleaned_data['position']
        catalog.summary = self.cleaned_data['summary']
        catalog.description = self.cleaned_data['description']
        catalog.save()
        for g in self.cleaned_data['groups']:
            catalog.groups.add(g)
        return catalog

