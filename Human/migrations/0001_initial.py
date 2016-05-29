# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
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
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
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
            ],
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField()),
                ('confirmed_time', models.DateTimeField(null=True)),
                ('created_time', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Privacy',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('link_me', models.BooleanField()),
                ('see_my_global', models.BooleanField()),
            ],
        ),
        migrations.AddField(
            model_name='link',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='link',
            name='group',
            field=models.ForeignKey(to='Human.Group'),
        ),
        migrations.AddField(
            model_name='link',
            name='source_member',
            field=models.ForeignKey(related_name='source_member', to='Human.GroupMember'),
        ),
        migrations.AddField(
            model_name='link',
            name='target_member',
            field=models.ForeignKey(related_name='target_member', to='Human.GroupMember'),
        ),
        migrations.AddField(
            model_name='groupmember',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='group',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='extra',
            name='privacy',
            field=models.ForeignKey(to='Human.Privacy'),
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
