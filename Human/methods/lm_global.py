#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/9
# Time: 13:52
import random
import networkx as nx

from Human.methods.graph import create_global_graph, graph_analyzer
from Human.models import GroupMember
from Human.models import Link
from LineMe.constants import CITIES_TABLE


def get_user_global_graph(user, groupid):
    # Todo: status should = 3
    ls = Link.objects.filter(group__id=groupid, status=3)

    nodes, links = [], []

    self = GroupMember.objects.get(group__id=groupid, user=user)
    nodes.append({'id': self.id, 'userid': self.user.id, 'name': self.member_name,
                  'self': True, 'group': 0})

    # Todo: implement group color
    gms = GroupMember.objects.filter(group__id=groupid).exclude(user=user)
    for gm in gms:
        nodes.append({'id': gm.id, 'userid': (-1 if gm.user is None else gm.user.id), 'name': gm.member_name,
                      'self': False, 'group': random.randint(1, 4)})

    if ls.count() != 0:

        G = create_global_graph(gms, ls, user)

        for s, t, d in G.edges_iter(data='created'):
            links.append({'source': s.id, 'target': t.id, 'status': d, 'value': 1})

    return {"nodes": nodes, "links": links}


def get_user_global_map(user, groupid):
    # Todo: status should =3
    ls = Link.objects.filter(group__id=groupid, status=3)
    gms = GroupMember.objects.filter(group__id=groupid)
    my_member = gms.get(group__id=groupid, user=user)

    G = create_global_graph(gms, ls, user)

    GMap = nx.Graph()

    for gm in gms:
        if gm.user is not None:
            g_l = gm.user.extra.location
            if g_l is not None:
                if not GMap.has_node(g_l):
                    GMap.add_node(g_l, weight=1, friends=0)
                else:
                    GMap.node[g_l]['weight'] += 1

    for friend in G.neighbors(my_member):
        if friend.user is not None:
            f_l = friend.user.extra.location
            if f_l is not None:
                GMap.node[f_l]['friends'] += 1

    if user.extra.location is not None:
        GMap.node[user.extra.location]['self'] = True

    # print GMap.nodes(data=True)

    for link in ls:
        if link.source_member.user is not None and link.target_member.user is not None:
            s_l = link.source_member.user.extra.location
            t_l = link.target_member.user.extra.location
            if s_l is not None and t_l is not None and s_l != t_l:
                if not GMap.has_edge(s_l, t_l):
                    GMap.add_edge(s_l, t_l)

    # print GMap.edges(data=True)

    nodes, links = [], []

    for (node, d) in GMap.nodes(data=True):
        # print d
        country, city = node.split('-')
        nodes.append({"name": city, "value": CITIES_TABLE[country][city][-1::-1] + [d['weight'], d['friends']],
                      "self": True if 'self' in d else False})

    # print nodes

    for (s, t) in GMap.edges():
        s_country, s_city = s.split('-')
        t_country, t_city = t.split('-')
        links.append({"source": s_city, "target": t_city})

    # print links

    return {"nodes": nodes, "links": links}


def get_user_global_info(user, groupid):
    return graph_analyzer(user, groupid)
