#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/4/12 
# Time: 21:26
#
from django import forms
from LineMe.constants import IDENTIFIER, GROUP_TYPE


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
