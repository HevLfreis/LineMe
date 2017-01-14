#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/10/7
# Time: 12:29
import datetime
import networkx as nx
from django.db.models import Q

from friendnet.models import Link, GroupMember


def global_core(G):
    for (s, t, d) in G.edges(data=True):
        # w = d['weight']
        # if w < 2:
        #     # print s.member_name, t.member_name
        #     G.remove_edge(s, t)
        #     c += 1
        s = GroupMember.objects.get(id=s)
        t = GroupMember.objects.get(id=t)
        links = Link.objects.filter((Q(source_member=s, target_member=t) | Q(source_member=t, target_member=s)), status=3, group__id=10001)
        couple = {s.user: False, t.user: False}

        for link in links:
            if link.creator in couple:
                # print couple, link.creator
                couple[link.creator] = True

        if not couple.values() == [True, True]:
            G.remove_edge(s.id, t.id)
        else:
            if d['ks'] - d['weight'] == -2:
                print s.id, t.id, d['ks'], d['weight']


    return G

    # for g in nx.connected_component_subgraphs(G):
    #     if g.number_of_nodes() > 1:
    #         print g.number_of_nodes(), g.number_of_edges()
    # print G.number_of_nodes(), G.number_of_edges()


def no_hub(G):
    for node in G.nodes():
        if G.degree(node) > 50:
            # for n in G_all_confirmed.neighbors(node):
            #     G_center.add_edge(node, n)
            G.remove_node(node)

    for g in nx.connected_component_subgraphs(G):
        if g.number_of_nodes() != 1:
            print g.number_of_nodes(), g.number_of_edges()


def only_hub(G):
    for s, t in G.edges():
        if G.degree(s) < 50 and G.degree(t) < 50:
            # for n in G_all_confirmed.neighbors(node):
            #     G_center.add_edge(node, n)
            G.remove_edge(s, t)

    for g in nx.connected_component_subgraphs(G):
        if g.number_of_nodes() != 1:
            print g.number_of_nodes(), g.number_of_edges()


def private_link(G):
    new_links = Link.objects.filter(group__id=10001, created_time__gt=datetime.datetime(2016, 10, 27, 10, 0, 0))

    G_new = build_graph_id(new_links)

    for s, t in G_new.edges():
        if G.has_edge(s, t):
            G.remove_edge(s, t)

    print G_new.number_of_edges(), G.number_of_edges()

    return G


def build_graph_id(links):
    G = nx.Graph()

    for link in links:
        s, t = link.source_member_id, link.target_member_id
        if not G.has_edge(s, t):
            G.add_edge(s, t, link=[link], weight=1)
        else:
            G[s][t]['weight'] += 1
            G[s][t]['link'].append(link)
    return G


def community_test(G, weight=8):

    # new_links = Link.objects.filter(group__id=10001, created_time__gt=datetime.datetime(2016, 10, 27, 10, 0, 0))
    #
    # G_new = build_graph_id(new_links)

    for s, t, d in G.edges(data=True):
        if G.has_edge(s, t):
            if d['ks'] < weight:
                G.remove_edge(s, t)

    for n in G.nodes():
        if G.degree(n) == 0:
            G.remove_node(n)

    print G.number_of_nodes(), G.number_of_edges()

    return G


def wrong(G):
    # s, t = 10041, 10069
    # s, t = 10110, 10115
    # s, t = 10265, 10046
    # s, t = 10263, 10112
    s, t = 10028, 10075

    print len(set(G.neighbors(s))), (len(G.neighbors(t)))
    G.remove_nodes_from(set(G.nodes()) - {t, s} - set(G.neighbors(s)) - set(G.neighbors(t)))

    for s1, t1, d in G.edges(data=True):
        if d['ks'] < 12:
            G.remove_edge(s1, t1)

        # if s1 == s or t1 == s or s1 == t or t1 == t:
        #     continue
        # else:
        #     G.remove_edge(s1, t1)

    G.add_edge(s, t, status=True, weight=1, id=100)

    return G
