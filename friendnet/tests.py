import json
import os
import networkx as nx
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

G = nx.Graph()
G.add_node(1)
G.add_node(2)
# G.add_edge(1, 2)
G.add_edge(3, 4)

d = [nx.average_shortest_path_length(g)
     for g in nx.connected_component_subgraphs(G)
     if g.number_of_nodes() > 1]
print sum(d) / len(d)
