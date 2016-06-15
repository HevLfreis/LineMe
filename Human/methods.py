#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/5/16 
# Time: 19:56
#
from collections import Counter
import json
import random
import re
import datetime
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.http import Http404
from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils import timezone
from Human.constants import GROUP_MAXSIZE, GROUP_CREATED_CREDITS_COST, SOURCE_LINK_CONFIRM_STATUS_TRANSITION_TABLE, \
    TARGET_LINK_CONFIRM_STATUS_TRANSITION_TABLE, SOURCE_LINK_REJECT_STATUS_TRANSITION_TABLE, \
    TARGET_LINK_REJECT_STATUS_TRANSITION_TABLE, CITIES_TABLE
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
        return first + ' ' + last


def get_user_groups(user):
    gms = GroupMember.objects.filter(user=user, is_joined=True)

    groups = [gm.group for gm in gms]

    return groups


def get_user_msgs(user):
    my_members = GroupMember.objects.filter(user=user)

    msgs = []
    for mm in my_members:
        # msgs += Link.objects.filter(Q(source_member=mm, status=0) |
        #                              Q(target_member=mm, status=0) |
        #                              Q(source_member=mm, status=2) |
        #                              Q(target_member=mm, status=1) |
        #                              Q(source_member=mm, status=-2) |
        #                              Q(source_member=mm, status=-1), ~Q(creator=user))

        msgs += Link.objects.filter((Q(source_member=mm) & (Q(status=0) | Q(status=2) | Q(status=-2))) |
                                    Q(target_member=mm) & (Q(status=0) | Q(status=1) | Q(status=-1)),
                                    ~Q(creator=user))

    return msgs


def get_user_msgs_count(user):
    my_members = GroupMember.objects.filter(user=user)

    count = 0
    for mm in my_members:
        count += Link.objects.filter((Q(source_member=mm) & (Q(status=0) | Q(status=2) | Q(status=-2))) |
                                     Q(target_member=mm) & (Q(status=0) | Q(status=1) | Q(status=-1)),
                                     ~Q(creator=user)).count()
    return count


def get_user_invs(user, group_name=None):
    if group_name:
        invs = Link.objects.filter(creator=user, group__group_name=group_name).order_by('-created_time')
    else:
        invs = Link.objects.filter(creator=user).order_by('-created_time')
    return invs


def get_user_ego_graph(user, groupid):
    ls = Link.objects.filter(group__id=groupid, creator=user)
    data = {}
    gms, nodes, links = [], [], []

    self = GroupMember.objects.get(group__id=groupid, user=user)
    nodes.append({'id': self.id, 'userid': self.user.id, 'name': self.member_name,
                  'self': True, 'group': 0})

    if ls.count() != 0:

        for link in ls:

            if link.source_member not in gms and link.source_member != self:
                gms.append(link.source_member)
            if link.target_member not in gms and link.target_member != self:
                gms.append(link.target_member)

        for gm in gms:
            nodes.append({'id': gm.id, 'userid': (-1 if gm.user is None else gm.user.id), 'name': gm.member_name,
                          'self': False, 'group': random.randint(1, 4)})

        for link in ls:
            links.append({'id': link.id, 'source': link.source_member.id, 'target': link.target_member.id,
                          'status': link.status, 'value': 1, 'group': link.group.id})

    data["nodes"] = nodes
    data["links"] = links

    return data


def get_user_global_graph(user, groupid):
    ls = Link.objects.filter(group__id=groupid)

    data = {}
    nodes, links = [], []

    self = GroupMember.objects.get(group__id=groupid, user=user)
    nodes.append({'id': self.id, 'userid': self.user.id, 'name': self.member_name,
                  'self': True, 'group': 0})

    gms = GroupMember.objects.filter(group__id=groupid).exclude(user=user)
    for gm in gms:
        nodes.append({'id': gm.id, 'userid': (-1 if gm.user is None else gm.user.id), 'name': gm.member_name,
                      'self': False, 'group': random.randint(1, 4)})

    if ls.count() != 0:

        G = global_graph(gms, ls, user)

        for s, t, d in G.edges_iter(data='created'):
            links.append({'source': s.id, 'target': t.id, 'status': d, 'value': 1})

        # for link in ls:
        #     links.append({'id': link.id, 'source': link.source_member.id, 'target': link.target_member.id,
        #                   'status': user == link.creator, 'value': 1, 'group': link.group.id})

    data["nodes"] = nodes
    data["links"] = links

    return data


def get_user_global_info(user, groupid):
    return graph_analyzer(user, groupid)


def get_group_joined_num(group):
    total = GroupMember.objects.filter(group=group).count()

    joined = GroupMember.objects.filter(group=group, is_joined=True).count()

    return str(joined) + '/' + str(total)


def get_user_joined(user, group):
    return GroupMember.objects.filter(user=user, group=group, is_joined=True).exists()


########################################################################

def check_profile(first_name, last_name, birth, sex, country, city, institution):
    if re.match("^[A-Za-z]+$", first_name) and re.match("^[A-Za-z]+$", last_name):
        if sex == 0 or sex == 1:
            if re.match("^(?:(?!0000)[0-9]{4}/(?:(?:0[1-9]|1[0-2])/(?:0[1-9]|1[0-9]|2[0-8])|"
                        "(?:0[13-9]|1[0-2])/(?:29|30)|(?:0[13578]|1[02])-31)|(?:[0-9]{2}(?:0[48]|"
                        "[2468][048]|[13579][26])|(?:0[48]|[2468][048]|[13579][26])00)/02/29)$", birth):
                if re.match("^[A-Za-z\s]+$", institution):
                    if country in CITIES_TABLE and city in CITIES_TABLE[country]:
                        return True
    return False


########################################################################

def check_groupid(groupid):
    if groupid is None:
        return -2
    elif Group.objects.filter(id=groupid).exists():
        return groupid
    else:
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
        u.extra.save()
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


# -----
def member_join(user, group, identifier):
    now = timezone.now()

    m = GroupMember.objects.get(group=group, member_name=get_user_name(user), token=identifier)
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

    for gm in GroupMember.objects.filter(group__id=groupid).exclude(user=user).order_by('-is_joined'):
        if gm not in gmin:
            gmout.append(gm)

    return gmout


########################################################################

def link_confirm(user, linkid):
    link = get_object_or_404(Link, id=linkid)

    gm = GroupMember.objects.get(user=user, group=link.group)

    if gm is not None:
        now = timezone.now()
        link.confirmed_time = now

        if link.source_member == gm:
            link.status = SOURCE_LINK_CONFIRM_STATUS_TRANSITION_TABLE[link.status]

        elif link.target_member == gm:
            link.status = TARGET_LINK_CONFIRM_STATUS_TRANSITION_TABLE[link.status]

        else:
            return -1
        # print 'confirm: ', linkid, link.status
        link.save()
        return 0
    else:
        return 1


def link_reject(user, linkid):
    link = get_object_or_404(Link, id=linkid)

    gm = GroupMember.objects.get(user=user, group=link.group)

    if gm is not None:
        now = timezone.now()
        link.confirmed_time = now

        if link.source_member == gm:
            link.status = SOURCE_LINK_REJECT_STATUS_TRANSITION_TABLE[link.status]

        elif link.target_member == gm:
            link.status = TARGET_LINK_REJECT_STATUS_TRANSITION_TABLE[link.status]

        else:
            return -1

        # print 'reject: ', linkid, link.status
        link.save()
        return 0
    else:
        return 1


# need check
def update_links(new_links, groupid, creator):
    old_links = Link.objects.filter(creator=creator, group__id=groupid)
    linksDict = {}

    for link in old_links:
        linksDict[str(link.source_member.id) + ',' + str(link.target_member.id)] = link

    for link in eval(new_links):
        if link["source"] + ',' + link["target"] in linksDict:
            linksDict[link["source"] + ',' + link["target"]] = 0
        elif link["target"] + ',' + link["source"] in linksDict:
            linksDict[link["target"] + ',' + link["source"]] = 0
        else:
            linksDict[link["source"] + ',' + link["target"]] = 1

    user_gmid = GroupMember.objects.get(group__id=groupid, user=creator).id

    for k, v in linksDict.items():
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


def global_graph(nodes, links, user):
    G = nx.Graph()

    # all members are calculated as nodes or only linked member are nodes
    for node in nodes:
        G.add_node(node)

    for link in links:
        if not G.has_edge(link.source_member, link.target_member):
            if link.creator == user:
                G.add_edge(link.source_member, link.target_member, weight=1, created=True)
            else:
                G.add_edge(link.source_member, link.target_member, weight=1)
        else:
            if link.creator == user:
                G[link.source_member][link.target_member]['weight'] += 1
                G[link.source_member][link.target_member]['created'] = True
            else:
                G[link.source_member][link.target_member]['weight'] += 1

    return G


def graph_analyzer(user, groupid):

    nodes = GroupMember.objects.filter(group__id=groupid)
    links = Link.objects.filter(group__id=groupid)
    my_member = nodes.get(user=user)

    G = global_graph(nodes, links, user)

    # print my_member

    # print G.edges(data=True)

    distribution = {k: v / float(G.number_of_nodes()) for k, v in dict(Counter(G.degree().values())).items()}

    # print distribution, dict(Counter(G.degree().values()))

    # distribution = {str(k): v for k, v in nx.degree_centrality(G)}

    top = sorted(G.degree().items(), key=lambda x: x[1], reverse=True)
    top3 = top[0:3]

    myRank = top.index((my_member, G.degree(my_member))) + 1

    # print top3, myRank

    myGraph = links.filter(creator=user).count()

    cover = myGraph / float(G.number_of_edges()) if not G.number_of_edges() == 0 else 0

    # print cover

    average_degree = 2 * G.number_of_edges() / G.number_of_nodes()

    # need fix !!!
    if nx.is_connected(G) and G.number_of_nodes() > 1:
        average_distance = nx.average_shortest_path_length(G)
    else:
        average_distance = 'INF'

    # print average_degree, average_distance

    friends = G.neighbors(my_member)

    friends = [(friend, G[friend][my_member]['weight']) for friend in friends]

    friends = sorted(friends, key=lambda x: x[1], reverse=True)

    # print friends
    # print friends[0][0].id
    if len(friends) > 0:
        bestfriend = friends[0][0]
        bf_ratio = friends[0][1] / float(G.number_of_nodes())
    else:
        bestfriend = None
        bf_ratio = 0

    # need fix!
    links_of_me = links.filter(Q(source_member=my_member) | Q(target_member=my_member)).exclude(creator=user)\
        .values('creator').annotate(count=Count('pk')).order_by('-count')

    # print links_of_me
    if len(links_of_me) != 0:

        heart = GroupMember.objects.get(user__id=links_of_me[0]['creator'], group__id=groupid)
        heart_count = links_of_me[0]['count']
    else:
        heart = None
        heart_count = None

    return {'distribution': json.dumps(distribution), 'top3': top3, 'my_rank': myRank,
            'average_degree': average_degree, 'average_distance': average_distance,
            'cover': cover,
            'bestfriend': bestfriend, 'bf_ratio': bf_ratio,
            'heart': heart, 'heart_count': heart_count}




