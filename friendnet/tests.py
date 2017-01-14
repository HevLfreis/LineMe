import json
import os
import random
from collections import Counter

import networkx as nx
import re
from django.test import TestCase

# Create your tests here.
# from Human.constants import STATIC_FOLDER
#
# j = json.load(file(os.path.join(STATIC_FOLDER, 'data/cities.json')))
#
# print j["People's Republic of China"]
# G = nx.Graph()
#
# G.add_edge(1, 2)
# G.add_edge(1, 3)
# G.add_edge(1, 4)
# print list(nx.resource_allocation_index(G, [(1,2),(1,3),(2,3),(1,4)]))

# for i in range(5):
#     print i
#     i += 1

a = {1:3}

def k(a):
    a[1] = 4


k(a)

print a

a = ['j ', 'k ']
print ','.join(a)
a = map(str.strip, a)
print ','.join(a)












