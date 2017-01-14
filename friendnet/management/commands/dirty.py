#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/10/20
# Time: 18:19
import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from friendnet.methods.basic.user import get_user_name
from friendnet.models import Link, Credit, GroupMember, Privacy


class Command(BaseCommand):
    help = 'Clean Links Credits'

    def handle(self, *args, **options):

        # GroupMember.objects.get(id=10108).delete()

        # old = [10330, 10336, 10338, 10339, 10341, 10345, 13208, 13209, 13211, 13212, 13213, 13214, 13215, 13216, 13220, 13221, 13222, 13224, 13225, 13226, 13227, 13231, 13235, 13242, 13244, 13246, 13248, 13252, 13253, 13256, 13259, 13266, 13271, 13273, 13274, 13278, 13285, 13291, 13292, 13295, 13297, 13300, 13302, 13303, 13304, 13305, 13307, 20567, 20568, 20569, 20570, 20571, 20572, 20573, 20574, 20575, 20576, 20577, 20578, 25380, 25381, 25382, 25383, 25384, 25385, 25386, 25387, 25388, 25389, 25390, 25391, 25392, 25393, 25394, 25395]
        # links = Link.objects.filter(creator=10046).order_by('id')
        # for link in links:
        #     print link, link.id
        #     if link.id not in old:
        #         link.delete()

        # print [link.id for link in links]
        # print link.source_member.member_name, link.target_member.member_name, get_user_name(link.creator)

        # u = User.objects.get(id=10215)
        # u.delete()
        for m in GroupMember.objects.filter(group__id=10008):
            print m.id, m.member_name




