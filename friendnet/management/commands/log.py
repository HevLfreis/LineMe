#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/10/18
# Time: 9:29
import re

from datetime import datetime
from django.core.management import BaseCommand

from friendnet.models import GroupMember


class Command(BaseCommand):
    help = 'Check logged member'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('-b', '--begin')
        parser.add_argument('-e', '--end')
        parser.add_argument('-g', '--group', type=int)

    def handle(self, *args, **options):

        start = datetime.strptime(options['begin'], '%Y-%m-%d')
        stop = datetime.strptime(options['end'], '%Y-%m-%d')

        print start, stop

        index = {}
        with open('logs/lineme.log') as f:
            for line in f:
                a = re.findall('\[.*?\]', line)
                t = datetime.strptime(a[0], '[%Y-%m-%d %H:%M:%S]')
                # print t
                b = a[1][1:-1].split(',')
                # print b

                if start < t < stop:
                    index[int(b[0])] = False

                    if 'update_links' in line or 'link_confirm':
                        index[int(b[0])] = True

        print len(index)

        members = GroupMember.objects.filter(group__id=options['group'])

        members_index = set([m.user.id for m in members if m.user is not None])

        print len(members_index)

        diff = members_index - set(index.keys())

        print len(diff)

        print 'No login: '
        for d in diff:
            print members.get(user__id=d).member_name, d

        print 'No opration: '
        for k, v in index.items():
            if not v:
                print members.get(user__id=k).member_name. d
