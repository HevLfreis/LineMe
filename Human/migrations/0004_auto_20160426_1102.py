# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Human', '0003_auto_20160426_1057'),
    ]

    operations = [

        migrations.AddField(
            model_name='link',
            name='from_member',
            field=models.ForeignKey(related_name='from_member', default=1, to='Human.GroupMember'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='link',
            name='to_member',
            field=models.ForeignKey(related_name='to_member', default=1, to='Human.GroupMember'),
            preserve_default=False,
        ),
    ]
