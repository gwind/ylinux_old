# coding: utf-8

from django import forms

from account.models import Permission,Group,User
from ydata.models import Category, Catalog, Topic, Post, Reputation, Report, Attachment, TZ_CHOICES, PRIVACY_CHOICES
from ydata import settings as ydata_settings


class PermissionForm(forms.ModelForm):
    class Meta:
        model = Permission

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        #fields = ['username','email','password']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'groups', 'position')

class CatalogForm(forms.ModelForm):
    class Meta:
        model = Catalog

