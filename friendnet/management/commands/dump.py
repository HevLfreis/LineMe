#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/11/30
# Time: 16:11
import os

from django.core.management import BaseCommand

from LineMe.settings import BASE_DIR
from friendnet.models import Link, GroupMember


class Command(BaseCommand):

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('-g', '--group', type=int)

    def handle(self, *args, **options):
        groupid = options['group']

        dump_dir = os.path.join(BASE_DIR, 'dump', str(groupid)+'.csv')
        members = GroupMember.objects.filter(group__id=groupid)
        with open(dump_dir, 'w') as f:
            f.write('source,target,creator,status,created_time,confirmed_time\n')

            for link in Link.objects.filter(group__id=groupid):
                print link.id
                text = [link.source_member_id, link.target_member_id, members.get(user=link.creator).id,
                        link.status, link.created_time, link.confirmed_time]
                f.write(','.join(map(str, text))+'\n')
