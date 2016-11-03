import json
import os
import random
from collections import Counter

import networkx as nx
import matplotlib.pyplot as plt
import re
from django.test import TestCase

# Create your tests here.
# from Human.constants import STATIC_FOLDER
#
# j = json.load(file(os.path.join(STATIC_FOLDER, 'data/cities.json')))
#
# print j["People's Republic of China"]

#
# def b(a):
#     a = a + 'm'
#
#
#
# a = 'm'
# b(a)
# print a

# ls = Link.objects.filter(
#     group__id=groupid,
#     status=3
# ).filter(Q(source_member__user=F('creator')) | Q(target_member__user=F('creator')))

# G = nx.Graph()
# G.add_node(1)
# G.add_node(2)
# # G.add_edge(1, 2)
# G.add_edge(3, 4)
#
# d = [nx.average_shortest_path_length(g)
#      for g in nx.connected_component_subgraphs(G)
#      if g.number_of_nodes() > 1]
# print sum(d) / len(d)

# G = nx.barabasi_albert_graph(100, 3)
# print sum(G.degree().values()) / float(G.number_of_nodes())
#
# print G.number_of_edges()

x, y = [], []
num_of_groups = 30
for i in xrange(2, num_of_groups):
    print i
    x.append(i)
    num_of_members = i
    it = 100

    sl = 0.0
    cnt = Counter()
    for j in xrange(it):
        G = nx.barabasi_albert_graph(num_of_groups * num_of_members, num_of_members)
        # G = nx.watts_strogatz_graph(num_of_groups * num_of_members, num_of_members, 0.3)
        # nx.draw(G)
        # plt.show()

        nodes = G.nodes()
        random.shuffle(nodes)

        group_index = {n: nodes.index(n) / num_of_members for n in G.nodes()}
        # print group_index

        G_group = nx.Graph()
        for s, t in G.edges():
            s, t = group_index[s], group_index[t]
            if G_group.has_edge(s, t):
                G_group[s][t]['weight'] += 1
            else:
                G_group.add_edge(s, t, weight=1)

        # print G_group.edges(), G.edges()

        for s, t, d in G_group.edges(data=True):
            # print s, t, d['weight']
            cnt[d['weight']] += 1
            # if d['weight'] < len(groups[s]) * len(groups[t]) / 2.0:
            #     G_group.remove_edge(s, t)

        average_weight = G.number_of_edges() / float(G_group.number_of_edges())
        sl += average_weight
        # print average_weight
        # # print G.number_of_edges() / float(G_group.number_of_edges()) / num_of_members
        # print '==='

    y.append(sl / it)
    print sl / it
    print sorted(cnt, key=cnt.get, reverse=True)
    print '======'

plt.plot(x, y)
plt.show()






