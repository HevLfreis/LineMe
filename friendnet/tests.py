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
G = nx.Graph()

G.add_edge(1, 2)
G.add_edge(1, 3)
print list(nx.resource_allocation_index(G))

# for i in range(5):
#     print i
#     i += 1












