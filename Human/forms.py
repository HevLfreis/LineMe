#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/4/12 
# Time: 21:26
#
from django import forms
from LineMe.constants import IDENTIFIER, GROUP_TYPE


class LoginForm(forms.Form):
    username = forms.CharField(max_length=40)
    password = forms.CharField(widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=40)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def cleaned_register(self):
        name = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']

        return name, email, password, password2


class GroupCreateForm(forms.Form):
    name = forms.CharField()
    CHOICES1 = tuple(IDENTIFIER.items())
    CHOICES2 = tuple(GROUP_TYPE.items())
    identifier = forms.CharField(widget=forms.Select(choices=CHOICES1))
    gtype = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES2)


class GroupMemberCreateForm(forms.Form):
    name = forms.CharField()
    identifier = forms.CharField()


class JoinForm(forms.Form):
    identifier = forms.CharField(required=True)


class FileUploadForm(forms.Form):
    members = forms.FileField()
