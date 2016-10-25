#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/10/20
# Time: 18:19
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from friendnet.methods.basic.user import get_user_name
from friendnet.models import Link, Credit, GroupMember


class Command(BaseCommand):
    help = 'Clean Links Credits'

    def handle(self, *args, **options):
        # GroupMember.objects.get(id=10157).delete()
        link = Link.objects.get(id=15587)
        print link.source_member.member_name, link.target_member.member_name, get_user_name(link.creator)