from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from django.test import TestCase

# Create your tests here.
import sys
import networkx as nx

# txt = 'HT'
# font = ImageFont.truetype('yahei.ttc',24)
# img = Image.new('RGB',(300,200),(255,255,255))
# draw = ImageDraw.Draw(img)
# draw.text( (0,50), 'HT',(0,0,0),font=font)
# draw.text((0,60),unicode('HT','utf-8'),(0,0,0),font=font)
# img.save('a.jpeg','JPEG')

# num = 10
# G = nx.barabasi_albert_graph(num+1, 2)
#
# for node in G.nodes():
#    if node == 0:
#        G.node[node]['name'] = 'hi'
#    else:
#        G.node[node]['name'] = 'no'+str(node)
#
# print G.nodes(data=True)
#
# for k, v in G.edges():
#     print G.node[k]['name'], G.node[v]['name']


a = {"a": 0}

print "a" in a