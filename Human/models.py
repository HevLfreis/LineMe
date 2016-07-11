from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Privacy(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # Todo: more privacy settings
    link_me = models.BooleanField()
    see_my_global = models.BooleanField()


class Extra(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    sex = models.BooleanField()
    birth = models.DateField()
    location = models.CharField(max_length=50, null=True)
    institution = models.CharField(max_length=150, null=True)
    privacy = models.ForeignKey(Privacy, on_delete=models.CASCADE)
    credits = models.IntegerField()


class Group(models.Model):
    group_name = models.CharField(max_length=50)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.IntegerField()
    maxsize = models.IntegerField()
    identifier = models.IntegerField()
    created_time = models.DateTimeField()
    deprecated = models.BooleanField()


class GroupMember(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    member_name = models.CharField(max_length=50)
    token = models.CharField(max_length=50)
    is_creator = models.BooleanField()
    is_joined = models.BooleanField()
    created_time = models.DateTimeField()
    joined_time = models.DateTimeField(null=True)


class MemberRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    message = models.CharField(max_length=200, null=True)
    created_time = models.DateTimeField()
    is_valid = models.BooleanField()


class Link(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    source_member = models.ForeignKey(GroupMember, related_name='source_member')
    target_member = models.ForeignKey(GroupMember, related_name='target_member')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    status = models.IntegerField()
    confirmed_time = models.DateTimeField(null=True)
    created_time = models.DateTimeField()


class Credits(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    link = models.ForeignKey(Link, on_delete=models.CASCADE, null=True)
    action = models.IntegerField()
    timestamp = models.DateTimeField()




