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
        group = options['group']
