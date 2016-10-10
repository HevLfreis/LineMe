#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/10/7
# Time: 12:29
import networkx as nx


def global_core(G):
    c = 0
    for (s, t, d) in G.edges(data=True):
        w = d['weight']
        if w < 2:
            # print s.member_name, t.member_name
            G.remove_edge(s, t)
            c += 1

    # print G.number_of_nodes(), G.number_of_edges(), c


def no_hub(G):
    for node in G.nodes():
        if G.degree(node) > 50:
            # for n in G_all_confirmed.neighbors(node):
            #     G_center.add_edge(node, n)
            G.remove_node(node)


def only_hub(G):
    for s, t in G.edges():
        if G.degree(s) < 50 and G.degree(t) < 50:
            # for n in G_all_confirmed.neighbors(node):
            #     G_center.add_edge(node, n)
            G.remove_edge(s, t)
