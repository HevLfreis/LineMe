#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/10/18
# Time: 9:29
import random
import re
from collections import Counter

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
        parser.add_argument('-i', '--interval')

    def handle(self, *args, **options):

        start = datetime.strptime(options['begin'], '%Y-%m-%d %H:%M:%S')
        if options['end']:
            stop = datetime.strptime(options['end'], '%Y-%m-%d %H:%M:%S')
        else:
            stop = datetime.now()

        print start, stop

        index = Counter()
        action = {}
        with open('logs/lineme.log') as f:
            for line in f:
                if 'Reset' in line:
                    continue
                a = re.findall('\[.*?\]', line)
                t = datetime.strptime(a[0], '[%Y-%m-%d %H:%M:%S]')
                # print t
                if len(a) < 2:
                    continue

                b = a[1][1:-1].split(',')
                mid = int(b[0])
                # print b

                if start < t < stop:
                    if 'update_links' in line or 'link_confirm' in line:
                        index[int(b[0])] += 1
                    act = re.findall('<.*?>', line)
                    if mid in action:
                        action[mid].append(act[0][1:-1].split(' ')[1])
                    else:
                        action[mid] = [act[0][1:-1].split(' ')[1]]

        # print random.sample(action.values(), 1)
        print len(index)

        members = GroupMember.objects.filter(group__id=options['group'])

        members_index = set([m.user.id for m in members if m.user is not None])

        print len(members_index)

        diff = members_index - set(index.keys())

        print len(diff)

        print 'No login: '
        for d in diff:
            print members.get(user__id=d).member_name, d

        print 'No operation: '
        for k, v in index.items():
            if v == 0 and members.filter(user__id=k).exists():
                print members.get(user__id=k).member_name, k

        # print 'Operation count: ', sum(index.values())

        for m in members:
            if m.user is not None:
                print m.member_name, index[m.user.id]

        c = Counter()
        for k, v in action.items():
            pre = ''
            for i, act in enumerate(v):
                if i < len(v) - 2:
                    if act == 'update_links' or act == 'link_confirm':
                        if v[i+1] != 'update_links' and v[i+1] != 'link_confirm':
                            c[v[i+1]] += 1

        print c



