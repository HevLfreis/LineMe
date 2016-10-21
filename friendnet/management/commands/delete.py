#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/10/20
# Time: 18:19
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from friendnet.models import Link, Credit, GroupMember


class Command(BaseCommand):
    help = 'Clean Links Credits'

    def handle(self, *args, **options):
        GroupMember.objects.get(id=10157).delete()