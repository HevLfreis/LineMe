#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/9
# Time: 13:53
import json
import random
from collections import Counter

import datetime
import networkx as nx
from django.db.models import Count, Q

from LineMe.constants import CITIES_TABLE
from friendnet.models import GroupMember
from friendnet.models import Link


class LGraph:
    def __init__(self, group):
        """
        All nodes in networkx graph are member ids
        Cache the members query by id to accelerate link operation
        """
        self.G = nx.Graph()
        self.user = None
        self.group = group
        self.members = GroupMember.objects.filter(group=group)
        self.me = None
        self.raw_links = Link.objects.filter(group=group)
        self.confirmed_raw_links = self.raw_links.filter(status=3)
        self.member_index = {m.id: m for m in self.members}
        self.member_user_index = {m.id: m.user.id if m.user else None for m in self.members}

    def __user_init(self, user):
        self.user = user
        self.me = self.__myself()

    def myself(self):
        if not self.user:
            return None

        return self.me

    def __myself(self):
        if not self.user:
            return None

        return self.members.get(
            user=self.user,
            is_joined=True
        )

    def get_member(self, mid):
        return self.member_index[mid]

    def __get_source_target(self, source, target):
        return self.member_index[source], self.member_index[target]

    def ego_builder(self, user):

        self.__user_init(user)

        self.G.add_node(self.me.id, creator=True, group=0)

        for link in self.raw_links.filter(creator=self.user):
            self.G.add_edge(link.source_member_id,
                            link.target_member_id,
                            id=link.id,
                            status=link.status,
                            ks=1)

        for node in self.G.nodes():
            if node != self.me.id:
                self.G.node[node]['group'] = random.randint(1, 4)

        return self

    def exp_builder(self, horizon):

        new_raw_links = self.raw_links.filter(created_time__gt=horizon)
        old_raw_links = self.raw_links.filter(created_time__lt=horizon, status=3)

        for member in self.members:
            self.G.add_node(member.id, creator=False, group=random.randint(1, 4))

        for link in old_raw_links:
            s, t = link.source_member_id, link.target_member_id
            if not self.G.has_edge(s, t):
                self.G.add_edge(s, t, id=link.id, weight=1, ks=0, status=False)
            else:
                self.G[s][t]['weight'] += 1

            su, tu = self.member_user_index[s], self.member_user_index[t]
            if link.creator_id == su or link.creator_id == tu:
                pass
            else:
                self.G[s][t]['ks'] += 1

        for link in new_raw_links:
            s, t = link.source_member_id, link.target_member_id
            if not self.G.has_edge(s, t):
                continue
            else:
                self.G[s][t]['weight'] += 1

                su, tu = self.member_user_index[s], self.member_user_index[t]
                if link.creator_id == su or link.creator_id == tu:
                    pass
                else:
                    self.G[s][t]['ks'] += 1

        return self

    def core_builder(self):

        for member in self.members:
            self.G.add_node(member.id, creator=False, group=random.randint(1, 4))

        for link in self.confirmed_raw_links:
            s, t = link.source_member_id, link.target_member_id
            if not self.G.has_edge(s, t):
                self.G.add_edge(s, t, id=link.id, weight=1, ks=0, status=False)
            else:
                self.G[s][t]['weight'] += 1

            su, tu = self.member_user_index[s], self.member_user_index[t]
            if link.creator_id == su or link.creator_id == tu:
                pass
            else:
                self.G[s][t]['ks'] += 1

        return self

    def core(self, user):

        self.__user_init(user)

        self.G.node[self.me.id]['creator'] = True

        for link in self.confirmed_raw_links.filter(creator=user):
            s, t = link.source_member_id, link.target_member_id
            self.G[s][t]['status'] = True

        return self

    def color(self):
        group_color = GraphAnalyzer(self).graph_communities()
        for node in self.G.nodes():
            if node in group_color:
                self.G.node[node]['group'] = group_color[node]
            else:
                self.G.node[node]['group'] = 9

        return self

    def map2dict(self):

        GMap = nx.Graph()
        location_index = {}

        for member in self.members:
            if member.user is not None:
                g_l = member.user.extra.location
                location_index[member.id] = g_l
                if g_l is not None:
                    if not GMap.has_node(g_l):
                        GMap.add_node(g_l, weight=1, friends=0)
                    else:
                        GMap.node[g_l]['weight'] += 1
            else:
                location_index[member.id] = None

        for friend in self.G.neighbors(self.me.id):
            f = self.get_member(friend)
            if f.user is not None:
                f_l = location_index[friend]
                if f_l is not None:
                    GMap.node[f_l]['friends'] += 1

        if self.user.extra.location is not None:
            GMap.node[self.user.extra.location]['self'] = True

        # print GMap.nodes(data=True)

        for link in self.confirmed_raw_links:
            s_l = location_index[link.source_member_id]
            t_l = location_index[link.target_member_id]
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

    def three2dict(self):

        # no layer, return myself
        if self.G.number_of_edges() == 0:
            return [{"nodes": [{'id': self.me.id,
                                'userid': self.user.id,
                                'name': self.me.member_name,
                                'self': True,
                                'group': 0}],
                    "links": []}]

        max_weight = max([d['ks'] for (s, t, d) in self.G.edges(data=True)])
        layers, data = {w: [] for w in xrange(max_weight+1)}, []

        for (s, t, d) in self.G.edges(data=True):
            for i in xrange(d['ks']+1):
                layers[i].append((s, t))

            # for i in xrange(max_weight+1-d['ks']):
            #     layers[i].append((s, t))

        for k, layer in layers.items():
            nodes, links = set([]), []

            for (s, t) in layer:
                s, t = self.__get_source_target(s, t)
                nodes.add(s)
                nodes.add(t)
                links.append({'source': s.id,
                              'target': t.id})

            data.append({"nodes": [{'id': node.id,
                                    'userid': (-1 if node.user is None else node.user.id),
                                    'name': node.member_name,
                                    'self': False,
                                    'group': random.randint(1, 4)} for node in nodes],
                         "links": links})

        return data

    def bingo(self):
        return self.G

    def proceeding(self, func):
        func(self.G)
        return self

    def cover(self):
        if self.raw_links and self.G.number_of_edges() != 0:
            return self.confirmed_raw_links.filter(creator=self.user).count() / float(self.G.number_of_edges())
        else:
            return 0

    def heart(self):

        # Todo: without status=3 is more interesting
        links_of_me = self.raw_links \
            .filter(Q(source_member=self.me) | Q(target_member=self.me))\
            .exclude(creator=self.user)

        if links_of_me.exists():
            sorted_links = links_of_me.values('creator').annotate(count=Count('pk')).order_by('-count')
            return self.members.get(user__id=sorted_links[0]['creator'])
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
            if node != self.me.id:
                n = self.member_index[node]
                nodes.append({'id': node,
                              'userid': (-1 if n.user is None else n.user.id),
                              'name': n.member_name,
                              'self': False,
                              'group': d['group']})

        for (s, t, d) in self.G.edges(data=True):
            links.append({'id': d['id'],
                          'source': s,
                          'target': t,
                          'status': d['status'],
                          'value': d['ks']})

        return {"nodes": nodes, "links": links}

    def jsonify(self):
        return json.dumps(self.dictify())


class GraphAnalyzer:
    def __init__(self, Graph):
        self.Graph = Graph
        self.G = Graph.bingo()
        self.me = Graph.myself()
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

    # Todo: move to a more complex algo
    def best_friend(self):
        friends = self.G.neighbors(self.me.id)

        if len(friends) == 0:
            return None, 0

        friends = [(friend, self.G[friend][self.me.id]['weight']) for friend in friends]
        sorted_friends = sorted(friends, key=lambda x: x[1], reverse=True)

        return self.Graph.get_member(sorted_friends[0][0]), sorted_friends[0][1]

    def graph_communities(self):
        communities = nx.k_clique_communities(self.G, 6)
        communities_index = {}
        for i, group in enumerate(communities):
            for member in group:
                communities_index[member] = i + 1

        return communities_index

    def embeddedness(self, memberid):
        if not self.G.has_node(memberid):
            return -1

        my_friends = set(self.G.neighbors(self.me.id))
        your_friends = set(self.G.neighbors(memberid))

        embeddedness = len(my_friends & your_friends)

        return embeddedness

    def embeddedness_max(self):

        neighbors = self.G.neighbors(self.me.id)

        if len(neighbors) == 0:
            return None

        embeddedness_list = {}

        for member in neighbors:
            embeddedness_list[member] = self.embeddedness(member)

        m = sorted(embeddedness_list, key=embeddedness_list.get, reverse=True)[0]
        return self.Graph.get_member(m)



