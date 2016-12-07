from __future__ import unicode_literals

from django.contrib.postgres.fields import JSONField
from django.db import models

# Create your models here.
from friendnet.models import Group, GroupMember


class QuestionTemplate(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, primary_key=True)
    authenticated = models.BooleanField()
    template = JSONField(default={})


class Question(models.Model):
    group_member = models.OneToOneField(GroupMember, on_delete=models.CASCADE, primary_key=True)
    content = JSONField()
