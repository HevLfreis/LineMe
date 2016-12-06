#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/11/30
# Time: 16:11
from django.core.management import BaseCommand

from friendnet.models import Link


class Command(BaseCommand):

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('-g', '--group', type=int)

    def handle(self, *args, **options):
        groupid = options['group']
        with open(str(groupid)+'.csv', 'w') as f:
            f.write('source,target,status,created,confirmed\n')

            for link in Link.objects.filter(group__id=groupid):
                text = [link.source_member_id, link.target_member_id, link.status, link.created_time, link.confirmed_time]
                f.write(','.join(map(str, text))+'\n')
