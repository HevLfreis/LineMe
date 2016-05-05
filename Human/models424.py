from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Human(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sex = models.BooleanField()
    birth = models.DateField()
    location = models.CharField(max_length=50, null=True)
    institution = models.CharField(max_length=150, null=True)
    privacy = models.ForeignKey(Privacy, on_delete=models.CASCADE)
    credits = models.IntegerField()


class Privacy(models.Model):
    link_me = models.BooleanField()
    see_my_global = models.BooleanField()


class Group(models.Model):
    group_name = models.CharField(max_length=50)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    type = models.IntegerField()
    maxsize = models.IntegerField()
    identifier = models.IntegerField()
    created_time = models.DateTimeField()
    deprecated = models.BooleanField()




class Message(models.Model):
    creator = models.IntegerField()
    from_who = models.IntegerField()
    to_who = models.IntegerField()
    group = models.CharField(max_length=50)
    from_confirmed = models.IntegerField()
    to_confirmed = models.IntegerField()
    created_time = models.DateTimeField()
    confirmed_time = models.DateTimeField()


# who refers to the id in GroupMember
class Link(models.Model):
    creator = models.IntegerField()
    from_id = models.IntegerField()
    to_id = models.IntegerField()
    from_who = models.IntegerField()
    to_who = models.IntegerField()
    groupid = models.IntegerField()
    status = models.IntegerField()
    confirmed_time = models.DateTimeField()
    created_time = models.DateTimeField()








class Credits(models.Model):
    userid = models.IntegerField()
    linkid = models.IntegerField()
    action = models.IntegerField()
    timestamp = models.DateTimeField()




