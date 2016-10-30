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

        start = datetime.strptime(options['begin'], '%Y-%m-%d %H:%M:%S')
        stop = datetime.strptime(options['end'], '%Y-%m-%d %H:%M:%S')

        print start, stop

        index = {}
        with open('logs/lineme.log') as f:
            for line in f:
                if 'Reset' in line:
                    continue
                a = re.findall('\[.*?\]', line)
                t = datetime.strptime(a[0], '[%Y-%m-%d %H:%M:%S]')
                # print t
                b = a[1][1:-1].split(',')
                # print b

                if start < t < stop:
                    if int(b[0]) not in index:
                        index[int(b[0])] = 0

                    elif 'update_links' in line or 'link_confirm' in line:
                        index[int(b[0])] += 1

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
            if v == 0 and members.filter(user__id=k).exists():
                print members.get(user__id=k).member_name, k

        print 'Operation count: ', sum(index.values())
