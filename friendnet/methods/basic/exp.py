#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/10/7
# Time: 12:29
import datetime
import networkx as nx
from django.db.models import Q

from friendnet.models import Link


def global_core(G):
    for (s, t, d) in G.edges(data=True):
        # w = d['weight']
        # if w < 2:
        #     # print s.member_name, t.member_name
        #     G.remove_edge(s, t)
        #     c += 1

        links = Link.objects.filter((Q(source_member=s, target_member=t) | Q(source_member=t, target_member=s)), status=3, group__id=10001)
        couple = {s.user: False, t.user: False}

        for link in links:
            if link.creator in couple:
                # print couple, link.creator
                couple[link.creator] = True

        if not couple.values() == [True, True]:
            G.remove_edge(s, t)

    for g in nx.connected_component_subgraphs(G):
        if g.number_of_nodes() > 1:
            print g.number_of_nodes(), g.number_of_edges()
    print G.number_of_nodes(), G.number_of_edges()


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
