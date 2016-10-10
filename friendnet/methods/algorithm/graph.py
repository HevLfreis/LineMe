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

from LineMe.constants import CITIES_TABLE
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

    def global_builder(self):

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

        return self

    def color(self):
        group_color = GraphAnalyzer(self.G, self.me).graph_communities()
        for node in self.G.nodes():
            if node in group_color:
                self.G.node[node]['group'] = group_color[node]
            else:
                self.G.node[node]['group'] = 9

        return self

    def map_dictify(self):
        gms = GroupMember.objects.filter(group=self.group)

        GMap = nx.Graph()
        location_index = {}

        for gm in gms:
            if gm.user is not None:
                g_l = gm.user.extra.location
                location_index[gm] = g_l
                if g_l is not None:
                    if not GMap.has_node(g_l):
                        GMap.add_node(g_l, weight=1, friends=0)
                    else:
                        GMap.node[g_l]['weight'] += 1

        for friend in self.G.neighbors(self.me):
            if friend.user is not None:
                # f_l = friend.user.extra.location
                f_l = location_index[friend]
                if f_l is not None:
                    GMap.node[f_l]['friends'] += 1

        if self.user.extra.location is not None:
            GMap.node[self.user.extra.location]['self'] = True

        # print GMap.nodes(data=True)

        for link in self.raw_links:
            if link.source_member.user is not None and link.target_member.user is not None:
                # s_l = link.source_member.user.extra.location
                # t_l = link.target_member.user.extra.location
                s_l = location_index[link.source_member]
                t_l = location_index[link.target_member]
                if s_l is not None and t_l is not None and s_l != t_l:
                    if not GMap.has_edge(s_l, t_l):
                        GMap.add_edge(s_l, t_l)

        # print GMap.edges(data=True)

        nodes, links = [], []

        for (node, d) in GMap.nodes(data=True):
            # print d
            country, city = node.split('-')
            nodes.append({"name": city,
                          "value": CITIES_TABLE[country][city][-1::-1] + [d['weight'], d['friends']],
                          "self": True if 'self' in d else False})

        # print nodes

        for (s, t) in GMap.edges():
            if (GMap.node[s]['friends'] != 0 and GMap.node[t]['friends'] != 0) or \
                    ('self' in GMap.node[s] and GMap.node[t]['friends'] != 0) or \
                    (GMap.node[s]['friends'] != 0 and 'self' in GMap.node[t]):
                s_country, s_city = s.split('-')
                t_country, t_city = t.split('-')
                links.append({"source": s_city, "target": t_city})

        # print links

        return {"nodes": nodes, "links": links}

    def bingo(self):
        return self.G

    def proceeding(self, func):
        func(self.G)
        return self

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

        for (node, d) in self.G.nodes(data='group'):
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

    # Todo: division zero warning
    def average_shortest_path_length(self):
        if self.number_of_edges < 2:
            return 1.0
        d = [nx.average_shortest_path_length(g)
             for g in nx.connected_component_subgraphs(self.G)
             if g.number_of_nodes() > 1]
        return sum(d) / len(d)

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
