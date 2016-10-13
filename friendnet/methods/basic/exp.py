#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/10/7
# Time: 12:29
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
