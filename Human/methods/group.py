#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/9
# Time: 13:50
import networkx as nx
from django.db.models import Q
from django.http import Http404
from django.utils import timezone

from Human.methods.groupmember import create_group_member
from Human.methods.session import get_session_id
from Human.methods.user import get_user_name
from Human.methods.utils import logger_join
from Human.methods.validation import validate_group_info, user_in_group
from Human.models import Group, Credits, MemberRequest, Link, Privacy
from Human.models import GroupMember
from LineMe.constants import GROUP_CREATED_CREDITS_COST
from LineMe.settings import logger


def create_group(request, user, name, identifier, gtype):
    now = timezone.now()

    if not validate_group_info(name, identifier, gtype):
        return -1
    elif user.extra.credits < GROUP_CREATED_CREDITS_COST:
        return -2

    try:

        g = Group(group_name=name.upper(),
                  creator=user,
                  type=gtype,
                  identifier=identifier,
                  created_time=now,
                  deprecated=False)
        g.save()

        m = GroupMember(group=g,
                        user=user,
                        member_name=get_user_name(user),
                        token="creator",
                        is_creator=True,
                        is_joined=True,
                        created_time=now,
                        joined_time=now)

        user.extra.credits -= GROUP_CREATED_CREDITS_COST

        c = Credits(user=user,
                    action=-GROUP_CREATED_CREDITS_COST,
                    timestamp=now)

        m.save()
        user.extra.save()
        c.save()

    except Exception, e:
        logger.error(logger_join('Create', get_session_id(request), 'failed', e=e))
        return -4

    # create dummy members
    # create_dummy_members(g, u, 20)
    #
    # # create dummy links
    # create_dummy_links(g, u, now)
    logger.info(logger_join('Create', get_session_id(request), gid=g.id))
    return 0


def group_recommender(user):

    if not user.privacy.allow_group_recommendation:
        return []

    gms = GroupMember.objects.filter(member_name=get_user_name(user), is_joined=False)

    sug = set(gm.group for gm in gms if not user_in_group(user, gm.group.id))

    return sug


def get_group_joined_num(group):
    total = GroupMember.objects.filter(group=group).count()

    joined = GroupMember.objects.filter(group=group, is_joined=True).count()

    return str(joined) + '/' + str(total)


def get_user_member_in_group(user, group):
    gm = GroupMember.objects.filter(
        (Q(member_name=get_user_name(user)) | Q(member_name=user.username)), group=group)
    if gm.exists():
        return gm
    else:
        return None


def get_user_join_status(request, user, group):

    join_failed = request.session.get('join_failed')
    if join_failed:
        del request.session['join_failed']

    joined = GroupMember.objects.filter(user=user, group=group, is_joined=True).exists()

    requested = MemberRequest.objects.filter(user=user, group=group, is_valid=True).exists()

    if joined:
        return 1
    elif join_failed:
        return -2
    elif requested:
        return -1
    else:
        return 0


# Todo: fix func
def group_privacy_check(user, group):
    if group.type == 1:
        if not get_user_member_in_group(user, group):
            raise Http404()


########################################################################

def create_dummy_members(group, u, num):
    for i in range(num):
        if u.username != 'test' + str(i):
            create_group_member(group, 'test' + str(i), 'test' + str(i) + '@123.com')


def create_dummy_links(group, user, now):
    num = GroupMember.objects.filter(group=group).count()
    G = nx.barabasi_albert_graph(num, 2)

    i = 0
    for node in G.nodes():
        if node == 0:
            G.node[node]['name'] = user.username
        else:
            G.node[node]['name'] = 'test' + str(i)
            i += 1

    for (f, t) in G.edges():
        link = Link(creator=user,
                    source_member=GroupMember.objects.get(member_name=G.node[f]['name'], group=group),
                    target_member=GroupMember.objects.get(member_name=G.node[t]['name'], group=group),
                    group=group,
                    status=0,
                    created_time=now)
        link.save()
