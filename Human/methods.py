#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/5/16 
# Time: 19:56
#
import re
import datetime
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from Human.constants import GROUP_MAXSIZE, GROUP_CREATED_CREDITS_COST
from Human.models import Privacy, Extra, GroupMember, Link, Group, Credits
from Human.utils import create_avatar
import networkx as nx


def create_user(name, email, password, password2):
    if user_existed(name):
        return 1
    elif not validate_email(email):
        return 2
    elif not validate_passwd(password, password2):
        return 3
    else:
        try:

            u = User.objects.create_user(name, email, password)
            u.save()
            pri = Privacy(user=u, link_me=True, see_my_global=True)
            pri.save()
            extra = Extra(user=u,
                          sex=False,
                          birth=datetime.date.today(),
                          credits=30,
                          privacy=pri)

            extra.save()
            create_avatar(u.id, name)
        except Exception, e:
            print 'Create user failed: ', e
            return 4

        return 0


def user_existed(name):
    if User.objects.filter(username=name).exists():
        return True
    return False


def validate_email(email):
    if User.objects.filter(email=email).exists():
        return False
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) is not None:
            return True
    return False


def validate_passwd(password, password2):
    if len(password) < 6 or password != password2:
        return False
    return True


########################################################################


def get_user_name(user):
    last = user.last_name
    first = user.first_name
    if len(first) is 0 and len(last) is 0:
        return user.username
    else:
        return last+' '+first


def get_user_groups(user):
    gms = GroupMember.objects.filter(user=user, is_joined=True)

    groups = [gm.group for gm in gms]

    return groups


def get_group_joined_num(group):
    total = GroupMember.objects.filter(group=group).count()

    joined = GroupMember.objects.filter(group=group, is_joined=True).count()

    return str(joined)+'/'+str(total)


########################################################################

def check_groupid(id):
    if id == '':
        return -2
    if Group.objects.filter(id=id).exists():
        return id
    return 0


def group_name_existed(name):
    if Group.objects.filter(group_name=name).exists():
        return True
    return False


def create_group(request, name, maxsize, identifier, type):
    u = request.user
    now = timezone.now()

    # -----
    if group_name_existed(name) or maxsize > GROUP_MAXSIZE or u.extra.credits < GROUP_CREATED_CREDITS_COST:
        return 1
    try:

        g = Group(group_name=name,
                  creator=u,
                  type=type,
                  maxsize=maxsize,
                  identifier=identifier,
                  created_time=now,
                  deprecated=False)
        g.save()

        m = GroupMember(group=g,
                        user=u,
                        member_name=get_user_name(u),
                        token="creator",
                        is_creator=True,
                        is_joined=True,
                        created_time=now,
                        joined_time=now)

        u.extra.credits -= GROUP_CREATED_CREDITS_COST

        c = Credits(user=u,
                    action=-GROUP_CREATED_CREDITS_COST,
                    timestamp=now)

        m.save()
        u.save()
        c.save()

    except Exception, e:
        print 'Group: ', e
        return 1

    # create dummy members
    # create_dummy_members(g, u, 20)
    #
    # # create dummy links
    # create_dummy_links(g, u, now)
    return 0


# group suggestion
def group_recommender(user):
    gms = GroupMember.objects.filter(member_name=get_user_name(user), is_joined=False)

    sug = [gm.group for gm in gms]

    return sug


# -----
def member_join(user, group, identifier):
    now = timezone.now()

    m = GroupMember.objects.get(group=group, member_name=user.username, token=identifier)
    m.is_joined = True
    m.user = user
    m.joined_time = now
    m.save()
    return 0


# group member suggestion
def member_recommender(user, groupid):
    if groupid == -2:
        return None
    gmout = []
    gmin = []
    ls = Link.objects.filter(group__id=groupid, creator=user)

    for l in ls:
        if l.source_member not in gmin or l.target_member not in gmin:
            gmin.append(l.source_member)
            gmin.append(l.target_member)

    for gm in GroupMember.objects.filter(group__id=groupid).exclude(user=user):
        if gm not in gmin:
            gmout.append(gm)

    return gmout


########################################################################

def create_group_member(group, name, identifier):

    now = timezone.now()

    if GroupMember.objects.filter(Q(member_name=name) | Q(token=identifier), group=group).exists():
        return 1

    try:
        m = GroupMember(group=group,
                        member_name=name,
                        token=identifier,
                        is_creator=False,
                        is_joined=False,
                        created_time=now)
        m.save()
    except Exception, e:
        print 'Group member create: ', e
        return 1
    return 0


########################################################################

def update_links(newLinks, groupid, creator):

    oldLinks = Link.objects.filter(creator=creator, group__id=groupid)
    LinksDict = {}

    for link in oldLinks:
        LinksDict[str(link.source_member.id)+','+str(link.target_member.id)] = link

    for link in eval(newLinks):
        if link["source"]+','+link["target"] in LinksDict:
            LinksDict[link["source"]+','+link["target"]] = 0
        elif link["target"]+','+link["source"] in LinksDict:
            LinksDict[link["target"]+','+link["source"]] = 0
        else:
            LinksDict[link["source"]+','+link["target"]] = 1

    user_gmid = GroupMember.objects.get(group__id=groupid, user=creator).id

    for k, v in LinksDict.items():
        if v is 0:
            continue
        elif v is 1:
            try:
                source = int(k.split(',')[0])
                target = int(k.split(',')[1])
                if source == user_gmid:
                    status = 1
                elif target == user_gmid:
                    status = 2
                else:
                    status = 0
                now = timezone.now()

                l = Link(creator=creator,
                         source_member_id=source,
                         target_member_id=target,
                         group_id=groupid,
                         status=status,
                         created_time=now)
                l.save()

            except Exception, e:
                print e
        else:
            v.delete()


########################################################################

def create_dummy_members(group, u, num):
    for i in range(num):
        if u.username != 'test'+str(i):
            create_group_member(group, 'test'+str(i), 'test'+str(i)+'@123.com')


def create_dummy_links(group, user, now):
    num = GroupMember.objects.filter(group=group).count()
    G = nx.barabasi_albert_graph(num, 2)

    i = 0
    for node in G.nodes():
        if node == 0:
            G.node[node]['name'] = user.username
        else:
            G.node[node]['name'] = 'test'+str(i)
            i += 1

    for (f, t) in G.edges():
        link = Link(creator=user,
                    source_member=GroupMember.objects.get(member_name=G.node[f]['name'], group=group),
                    target_member=GroupMember.objects.get(member_name=G.node[t]['name'], group=group),
                    group=group,
                    status=0,
                    created_time=now)
        link.save()

