#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/4/12 
# Time: 21:26
#
from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    name = forms.CharField(label='Acount name', max_length=40)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)


class GroupCreateForm(forms.Form):
    name = forms.CharField()
    maxsize = forms.IntegerField()
    CHOICES = (
        ('0', 'Email'),
        ('1', 'Institution'),
        ('2', 'Special Code'),
    )
    identifier = forms.CharField(widget=forms.Select(choices=CHOICES))


class GroupMemberCreateForm(forms.Form):
    name = forms.CharField()
    identifier = forms.CharField()


class ReJoinIdentifierForm(forms.Form):
    groupid = forms.CharField()
    identifier = forms.CharField(required=True)