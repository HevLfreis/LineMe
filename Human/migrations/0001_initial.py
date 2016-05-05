# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Credits',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.IntegerField()),
                ('timestamp', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Extra',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sex', models.BooleanField()),
                ('birth', models.DateField()),
                ('location', models.CharField(max_length=50, null=True)),
                ('institution', models.CharField(max_length=150, null=True)),
                ('credits', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_name', models.CharField(max_length=50)),
                ('type', models.IntegerField()),
                ('maxsize', models.IntegerField()),
                ('identifier', models.IntegerField()),
                ('created_time', models.DateTimeField()),
                ('deprecated', models.BooleanField()),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GroupMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('member_name', models.CharField(max_length=50)),
                ('token', models.CharField(max_length=50)),
                ('is_creator', models.BooleanField()),
                ('is_joined', models.BooleanField()),
                ('created_time', models.DateTimeField()),
                ('joined_time', models.DateTimeField(null=True)),
                ('group', models.ForeignKey(to='Human.Group')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField()),
                ('confirmed_time', models.DateTimeField()),
                ('created_time', models.DateTimeField()),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('from_user', models.ForeignKey(related_name='from_user', to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(to='Human.Group')),
                ('to_user', models.ForeignKey(related_name='to_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Privacy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('link_me', models.BooleanField()),
                ('see_my_global', models.BooleanField()),
            ],
        ),
        migrations.AddField(
            model_name='extra',
            name='privacy',
            field=models.ForeignKey(to='Human.Privacy'),
        ),
        migrations.AddField(
            model_name='extra',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='credits',
            name='link',
            field=models.ForeignKey(to='Human.Link', null=True),
        ),
        migrations.AddField(
            model_name='credits',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
