#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/4/12 
# Time: 21:26
#
from django import forms
from Human.constants import IDENTIFIER, GROUP_TYPE


class LoginForm(forms.Form):
    username = forms.CharField(max_length=40)
    password = forms.CharField(widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=40)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)


class GroupCreateForm(forms.Form):
    name = forms.CharField()
    maxsize = forms.IntegerField()
    CHOICES1 = tuple(IDENTIFIER.items())
    CHOICES2 = tuple(GROUP_TYPE.items())
    identifier = forms.CharField(widget=forms.Select(choices=CHOICES1))
    type = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES2)


class GroupMemberCreateForm(forms.Form):
    name = forms.CharField()
    identifier = forms.CharField()


class ReJoinIdentifierForm(forms.Form):
    identifier = forms.CharField(required=True)


class FileUploadForm(forms.Form):
    members = forms.FileField()
