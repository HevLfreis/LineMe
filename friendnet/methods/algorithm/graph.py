#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/9
# Time: 13:53
import json
import random
from collections import Counter

import networkx as nx
from django.db.models import Count, Q

from friendnet.models import GroupMember, Group
from friendnet.models import Link


class Graph:
    def __init__(self, user, group):
        self.G = nx.Graph()
        self.user = user
        self.group = group
        self.me = self.__myself()
        self.raw_links = None

    def myself(self):
        return self.me

    def __myself(self):
        return GroupMember.objects.get(
            group=self.group,
            user=self.user,
            is_joined=True
        )

    def ego_builder(self):

        self.raw_links = Link.objects.filter(
            group=self.group,
            creator=self.user
        )

        self.G.add_node(self.me, creator=True, group=0)

        for link in self.raw_links:
            self.G.add_edge(link.source_member,
                            link.target_member,
                            id=link.id,
                            status=link.status,
                            weight=1)

        for node in self.G.nodes():
            if node != self.me:
                self.G.node[node]['group'] = random.randint(1, 4)

        return self

    def global_builder(self, color=False):

        self.raw_links = Link.objects.filter(
            group=self.group,
            status=3
        )

        members = GroupMember.objects.filter(group=self.group).exclude(user=self.user)

        self.G.add_node(self.me, creator=True)
        for member in members:
            self.G.add_node(member, creator=False, group=random.randint(1, 4))

        for link in self.raw_links:
            if not self.G.has_edge(link.source_member, link.target_member):
                if link.creator == self.user:
                    self.G.add_edge(link.source_member, link.target_member, id=link.id, weight=1, status=True)
                else:
                    self.G.add_edge(link.source_member, link.target_member, id=link.id, weight=1, status=False)
            else:
                if link.creator == self.user:
                    self.G[link.source_member][link.target_member]['weight'] += 1
                    self.G[link.source_member][link.target_member]['status'] = True
                else:
                    self.G[link.source_member][link.target_member]['weight'] += 1

        if color:
            group_color = GraphAnalyzer(self.G, self.me).graph_communities()
            for node in self.G.nodes():
                if node in group_color:
                    self.G.node[node]['group'] = group_color[node]
                else:
                    self.G.node[node]['group'] = 9

        return self

    def bingo(self):
        return self.G

    def cover(self):
        if self.raw_links and self.G.number_of_edges() != 0:
            return self.raw_links.filter(creator=self.user).count() / float(self.G.number_of_edges())
        else:
            return 0

    def heart(self):
        links_of_me = self.raw_links \
            .filter(Q(source_member=self.me) | Q(target_member=self.me))\
            .exclude(creator=self.user) \
            .values('creator').annotate(count=Count('pk')).order_by('-count')

        if len(links_of_me) != 0:
            return GroupMember.objects.get(user__id=links_of_me[0]['creator'], group=self.group)
        else:
            return None

    def dictify(self):

        nodes, links = [], []

        nodes.append({'id': self.me.id,
                      'userid': self.user.id,
                      'name': self.me.member_name,
                      'self': True,
                      'group': 0})

        for node, d in self.G.nodes(data='group'):
            if node != self.me:
                nodes.append({'id': node.id,
                              'userid': (-1 if node.user is None else node.user.id),
                              'name': node.member_name,
                              'self': False,
                              'group': d['group']})

        for (s, t, d) in self.G.edges(data=True):
            links.append({'id': d['id'],
                          'source': s.id,
                          'target': t.id,
                          'status': d['status'],
                          'value': d['weight']})

        return {"nodes": nodes, "links": links}

    def jsonify(self):
        return json.dumps(self.dictify())


class GraphAnalyzer:
    def __init__(self, G, me):
        self.G = G
        self.me = me
        self.number_of_nodes = self.G.number_of_nodes()
        self.number_of_edges = self.G.number_of_edges()

    def average_degree(self):
        return 2.0 * self.number_of_edges / self.number_of_nodes

    def sorted_degree(self):
        return sorted(self.G.degree().items(), key=lambda x: x[1], reverse=True)

    def degree_distribution(self):
        return {k: v / float(self.number_of_nodes) for k, v in dict(Counter(self.G.degree().values())).items() if k != 0}

    def average_distance(self):
        if nx.is_connected(self.G) and self.number_of_nodes > 1:
            return nx.average_shortest_path_length(self.G)
        else:
            return -1

    def best_friend(self):
        friends = self.G.neighbors(self.me)
        friends = [(friend, self.G[friend][self.me]['weight']) for friend in friends]
        sorted_friends = sorted(friends, key=lambda x: x[1], reverse=True)

        if len(sorted_friends) > 0:
            return sorted_friends[0][0], sorted_friends[0][1] / float(self.number_of_nodes)
        else:
            return None, 0

    def graph_communities(self):
        communities = nx.k_clique_communities(self.G, 3)
        communities_index = {}
        for i, group in enumerate(communities):
            for member in group:
                communities_index[member] = i + 1

        return communities_index


def create_global_graph(nodes, links, user):
    G = nx.Graph()

    # Todo: all members are calculated as nodes or only linked member are nodes
    for node in nodes:
        G.add_node(node)

    for link in links:
        if not G.has_edge(link.source_member, link.target_member):
            if link.creator == user:
                G.add_edge(link.source_member, link.target_member, weight=1, created=True)
            else:
                G.add_edge(link.source_member, link.target_member, weight=1)
        else:
            if link.creator == user:
                G[link.source_member][link.target_member]['weight'] += 1
                G[link.source_member][link.target_member]['created'] = True
            else:
                G[link.source_member][link.target_member]['weight'] += 1

    return G

# def graph_communities(G):
#     a = nx.k_clique_communities(G, 3)
#     group_index = {}
#     for i, g in enumerate(a):
#         for m in g:
#             group_index[m] = i + 1
#
#     return group_index


# Todo: link status should be 3
# Todo: most contributor ? get most credits
def graph_analyzer(user, groupid):

    Global = Graph(user, Group.objects.get(id=groupid)).global_builder()
    G = Global.bingo()
    my_member = Global.myself()
    analyzer = GraphAnalyzer(G, my_member)

    distribution = analyzer.degree_distribution()

    top = analyzer.sorted_degree()
    top3 = top[0:3]

    rank = top.index((my_member, G.degree(my_member))) + 1

    cover = Global.cover()

    # Todo: fix 0.00 ??
    average_degree = analyzer.average_degree()

    # If the network is not connected,
    # return -1
    # Todo: warning, when the net is big, very slow !!!!
    average_distance = analyzer.average_distance()

    best_friend, bf_ratio = analyzer.best_friend()

    # Todo: ratio not correct fixed...
    heart = Global.heart()

    return {'distribution': json.dumps(distribution),
            'top3': top3,
            'my_rank': rank,
            'average_degree': average_degree,
            'average_distance': average_distance,
            'cover': round(cover*100, 2),
            'bestfriend': best_friend,
            'bf_ratio': round(bf_ratio*100, 2),
            'heart': heart}
