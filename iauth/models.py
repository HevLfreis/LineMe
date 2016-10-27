from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class ResetToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    token = models.CharField(max_length=100)
    expired = models.DateTimeField()
    completed = models.BooleanField(default=False)
