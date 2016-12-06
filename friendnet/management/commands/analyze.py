#!/usr/bin/env python
# coding: utf-8
import copy
import csv
import datetime
import json
import random
from collections import Counter

import math
from itertools import product

import networkx as nx
import operator

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q, F

from LineMe.constants import PROJECT_NAME
# from friendnet.methods.algorithm.graph import Graph
from LineMe.settings import BASE_DIR
from friendnet.methods.algorithm.graph import Graph
from friendnet.methods.basic.user import get_user_name
from friendnet.models import Link, Group, GroupMember
import numpy as np


class Command(BaseCommand):
    help = 'Analysis Links of ' + PROJECT_NAME
    members = None
    y = []
    horizon = None
    groups = None
    member_user_index = {}

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('-g', '--group', type=int)

    def handle(self, *args, **options):
        self.analyzer(options['group'])

        return

    def analyzer(self, groupid):
        self.members = GroupMember.objects.filter(group__id=groupid)
        self.member_user_index = {m.id: m.user.id for m in self.members if m.user is not None}

        male_count = self.members.filter(user__extra__gender=False).count()
        female_count = self.members.filter(user__extra__gender=True).count()

        print male_count, female_count

        links = Link.objects.filter(group__id=groupid)
        friend_links = links.filter(Q(source_member__user=F('creator')) | Q(target_member__user=F('creator')))
        other_links = links.exclude(Q(source_member__user=F('creator')) | Q(target_member__user=F('creator')))

        links_male = friend_links.filter(creator__extra__gender=False)
        links_female = friend_links.filter(creator__extra__gender=True)

        print 'total links: ', links.count()
        print 'friend links: ', friend_links.count()
        print 'other links: ', other_links.count(), '\n'

        links_confirmed = self.confirmed(links)
        friend_links_confirmed = self.confirmed(friend_links)
        other_links_confirmed = self.confirmed(other_links)

        print 'total links confirmed: ', links_confirmed.count()
        print 'friend links confirmed: ', friend_links_confirmed.count()
        print 'other links confirmed: ', other_links_confirmed.count(), '\n'

        links_unconfirmed = self.unconfirmed(links)
        friend_links_unconfirmed = self.unconfirmed(friend_links)
        other_links_unconfirmed = self.unconfirmed(other_links)

        print 'total links unconfirmed: ', links_unconfirmed.count()
        print 'friend links unconfirmed: ', friend_links_unconfirmed.count()
        print 'other links unconfirmed: ', other_links_unconfirmed.count(), '\n'

        links_s_rejected = self.single_rejected(links)
        links_b_rejected = self.both_rejected(links)
        print 'single reject: ', links_s_rejected.count()
        print 'both reject: ', links_b_rejected.count(), '\n'

        print 'average added friends male: ', links_male.count() / float(male_count)
        print 'average added friends female: ', links_female.count() / float(female_count)
        print 'average added friends: ', friend_links.count() / float(self.members.count()), '\n'

        self.horizon = datetime.datetime(2016, 10, 27, 10, 0, 0)
        links_new = self.after_time(links, self.horizon)
        links_old = self.before_time(links, self.horizon)
        print 'new/old links count: ', links_new.count(), links_old.count(), '\n'

        print self.single_rejected(links_old).count(), self.both_rejected(links_old).count()

        # G_all = self.build_graph_id(links)
        # G_friend = self.build_graph(friend_links)
        # G_other = self.build_graph(other_links)
        #
        G_all_confirmed = self.build_graph_id(links_confirmed)
        # G_friend_confirmed = self.build_graph(friend_links_confirmed)
        # G_other_confirmed = self.build_graph(other_links_confirmed)

        # G_all_unconfirmed = self.build_graph_id(links_unconfirmed)
        # G_friend_unconfirmed = self.build_graph(friend_links_unconfirmed)
        # G_other_unconfirmed = self.build_graph(other_links_unconfirmed)

        self.print_info(G_all_confirmed, 'confirmed')

        print sum([self.embeddedness(G_all_confirmed, s, t) for s, t in G_all_confirmed.edges()]) / float(G_all_confirmed.number_of_edges())

        # for i in xrange(3, 20):
        #     c = list(nx.k_clique_communities(G_all_confirmed, i))
        #     print i, len(c), self.modularity(G_all_confirmed, c)

        # cnt1 = Counter()
        # # cnt2 = Counter()
        # #
        # user_member_index = {m.user.id: m.id for m in self.members}
        #
        # for s, t, d in G_all_confirmed.edges(data=True):
        #     weight = d['ks']
        #     links = d['link']
        #     cnt1[weight] += 1
        #
        #     neighbors = set(G_all_confirmed.neighbors(s)) | set(G_all_confirmed.neighbors(t))
        #     # print neighbors
        #
        #
        # print [[k, v] for k, v in cnt1.items()]
        # print [[k, v / float(G_all_confirmed.number_of_edges())] for k, v in cnt1.items()]
        # print sum([k * v for k, v in cnt1.items()])
        # print [[k, v / cnt1[k]] for k, v in cnt2.items()]

        # c_15 = list(nx.k_clique_communities(G_all_confirmed, 15))
        #
        # for a in c_15:
        #     print ' '.join([m.member_name for m in GroupMember.objects.filter(id__in=a)])
        #     print '---'

        # print self.variance([1 for i in xrange(100)])
        # print self.variance([i for i in xrange(100)])

        max_weight = max([d['ks'] for s, t, d in G_all_confirmed.edges(data=True)])
        # #
        # e = []
        # v = []
        # for j in xrange(0, max_weight):
        #     G_weight = G_all_confirmed.copy()
        #     for s, t, d in G_all_confirmed.edges(data=True):
        #         if d['ks'] < j:
        #             G_weight.remove_edge(s, t)
        #
        #     embed_list = [self.embeddedness(G_weight, s, t) for s, t, d in G_weight.edges(data=True)]
        #
        #     embed = sum(embed_list) / float(G_weight.number_of_edges())
        #     var = self.variance(embed_list)
        #     e.append(embed)
        #     v.append(var)
        #     print embed, var
        #
        # print e
        # print v

        # #
        all_module = []

        # for i in [k for k in xrange(15)][2::3]:
        # for i in [k for k in xrange(15)][2:]:
        #     print i
        #     module = []
        #     l = []
        #     for j in xrange(0, max_weight):
        #         G_weight = G_all_confirmed.copy()
        #         for s, t, d in G_all_confirmed.edges(data=True):
        #             if d['ks'] < j:
        #                 G_weight.remove_edge(s, t)
        #
        #         print G_weight.number_of_edges()
        #
        #         c = list(nx.k_clique_communities(G_weight, i+1))
        #         l.append(len(c))
        #
        #         m = self.modularity(G_all_confirmed, c)
        #         module.append(m)
        #         print j, m
        #
        #     print module
        #     print l
        #     all_module.append(module)

        # for i in xrange(0, max_weight):
        #     print i
        #     module = []
        #     l = []
        #
        #     G_weight = G_all_confirmed.copy()
        #     for s, t, d in G_all_confirmed.edges(data=True):
        #         if d['ks'] < i:
        #             G_weight.remove_edge(s, t)
        #
        #     print G_weight.number_of_edges()
        #
        #     for j in [k for k in xrange(15)][2:]:
        #
        #         c = list(nx.k_clique_communities(G_weight, j+1))
        #         l.append(len(c))
        #
        #         m = self.modularity(G_weight, c)
        #         module.append(m)
        #         print j, m
        #
        #     print module
        #     print l
        #
        #     max_module = max(module)
        #     all_module.append([max_module, module.index(max_module)])
        #
        # print all_module

        # k_k = [9,11,7,7,6,5,5,4,4,4,4]

        # k_weight = [(15, 0), (13, 1), (9, 3), (7, 5), (6, 6), (4, 7), (3, 11)]
        #
        # for k, w in k_weight:
        #     G_weight = G_all_confirmed.copy()
        #     for s, t, d in G_all_confirmed.edges(data=True):
        #         if d['ks'] < w:
        #             G_weight.remove_edge(s, t)
        #
        #     c = list(nx.k_clique_communities(G_weight, k))
        #
        #     print len(c)
        #
        #     comm_links = 0.0
        #     for m in xrange(len(c)):
        #         for n in xrange(m+1, len(c)):
        #             for a in c[m]:
        #                 for b in c[n]:
        #                     if G_weight.has_edge(a, b):
        #                         comm_links += 1
        #
        #     print comm_links / len(c) / (len(c) - 1) * 2



        # print G_all_confirmed.number_of_edges() / float(G_all.number_of_edges())
        #
        # for s, t in G_all_confirmed.edges():
        #     G_all.remove_edge(s, t)
        #
        # self.print_info(G_all, 'unconfirmed')
        # # self.print_info(G_all_unconfirmed, 'unconfirmed')
        #
        # sorted_degree = sorted(G_all.degree(), key=G_all.degree().get, reverse=True)
        #
        # for n in sorted_degree[:10]:
        #     print GroupMember.objects.get(id=n), G_all.degree(n)
        #
        # print '==='
        #
        # cnt = Counter()
        # for link in self.unconfirmed_not_reject(links_unconfirmed):
        #     if link.status == 2:
        #         cnt[link.source_member_id] += 1
        #     elif link.status == 1:
        #         cnt[link.target_member_id] += 1
        #     else:
        #         cnt[link.source_member_id] += 1
        #         cnt[link.target_member_id] += 1
        #
        # for k, v in cnt.items():
        #     print GroupMember.objects.get(id=k), v
        #
        # print sum([v for k, v in cnt.items()])

        # c = list(nx.k_clique_communities(G_all_confirmed, 15))
        # print self.modularity(G_all_confirmed, c)
        # for clique in c:
        #     # print clique
        #     print len(clique)
        #     print ' '.join([GroupMember.objects.get(id=node).member_name for node in clique])
        #
        # cliques = []
        # for clique in list(nx.find_cliques(G_all_confirmed)):
        #     if set(clique) not in cliques:
        #         cliques.append(set(clique))
        #
        # print len(cliques)
        #
        # cnt = Counter([len(c) for c in cliques])
        # print [[k, v] for k, v in cnt.items()]
        #
        # sorted_cliques = sorted(cliques, key=lambda x: len(x), reverse=True)
        #
        # # for clique in sorted_cliques:
        # #     print ' '.join([GroupMember.objects.get(id=node).member_name for node in clique])
        #
        # print len(sorted_cliques)
        #
        # for j in xrange(2, 12):
        #
        #     new_cliques = []
        #     base = sorted_cliques[0]
        #     for i in xrange(1, len(sorted_cliques)):
        #
        #         # print ' '.join([GroupMember.objects.get(id=node).member_name for node in clique])
        #         c1 = sorted_cliques[i]
        #         if len(c1 - base) <= j:
        #             base = base | c1
        #         else:
        #             new_cliques.append(base)
        #             base = c1
        #
        #         # print len(new_cliques)
        #     # new_cliques.append(base)
        #     # print ' '.join([GroupMember.objects.get(id=node).member_name for node in base])
        #     # print '====='
        #
        #     # sorted_cliques = sorted(new_cliques, key=lambda x: len(x), reverse=True)
        #     sorted_cliques = new_cliques
        #
        #     # if len(sorted_cliques) < 200:
        #     #     for clique in sorted_cliques:
        #     #         print ' '.join([GroupMember.objects.get(id=node).member_name for node in clique]), len(clique)
        #     #     print '====='
        #
        #     # print len(sorted_cliques)
        #
        #     # for clique in sorted_cliques:
        #     #     print ' '.join([GroupMember.objects.get(id=node).member_name for node in clique])
        #     #
        #
        #     print len(sorted_cliques)
        #
        # for clique in sorted_cliques:
        #     print ' '.join([GroupMember.objects.get(id=node).member_name for node in clique])
        #
        # print "==="
        #
        # final_cliques = {i: c for i, c in enumerate(sorted_cliques)}
        #
        # for k1, v1 in final_cliques.items():
        #     for k2, v2 in final_cliques.items():
        #         # print k1, k2
        #         if k1 < k2:
        #             if len(v1 - v2) < 5:
        #                 final_cliques[k1] = v1 | v2
        #                 del final_cliques[k2]
        #
        # print len(final_cliques)
        # final_cliques = final_cliques.values()
        #
        #
        # # for clique in final_cliques:
        # #     print ' '.join([GroupMember.objects.get(id=node).member_name for node in clique])
        #
        # for i in xrange(1, len(final_cliques)):
        #     for j in xrange(i):
        #         final_cliques[i] -= final_cliques[j]
        #
        # final_cliques = filter(lambda x: len(x) != 0, final_cliques)
        #
        # print 'module: ', self.modularity(G_all_confirmed, final_cliques)
        #
        # for clique in final_cliques:
        #     print ' '.join([GroupMember.objects.get(id=node).member_name for node in clique]), len(clique)
        # #
        # # # print sum([len(a) for a in final_cliques.values()])
        #
        # other_members = set(G_all_confirmed.nodes()) - set([n for clique in final_cliques for n in clique])
        #
        # print ' '.join([GroupMember.objects.get(id=node).member_name for node in other_members]), len(other_members)
        #
        # other_index = {}
        # for m in other_members:
        #     maxi, maxe = len(final_cliques), 0
        #     for i, clique in enumerate(final_cliques):
        #         embed = len(set(G_all_confirmed.neighbors(m)) & clique)
        #         # print embed
        #         if embed > maxe and embed > len(clique) / 5:
        #             maxi = i
        #
        #     other_index[m] = maxi
        #
        # print ' '.join([GroupMember.objects.get(id=node).member_name+' '+str(v) for node, v in other_index.items()])
        #
        # final_cliques.append(set([]))
        # for k, v in other_index.items():
        #     # if v == len(final_cliques):
        #     #     continue
        #     final_cliques[v].add(k)
        #
        # print sum([len(n) for n in final_cliques])
        # print 'module: ', self.modularity(G_all_confirmed, final_cliques)
        #
        # for clique in final_cliques:
        #     print ' '.join([GroupMember.objects.get(id=node).member_name for node in clique]), len(clique)

        #############################################################################
        #############################################################################
        #############################################################################
        # crowdsourcing

        links_confirmed_old = self.before_time(links_confirmed, self.horizon)
        #
        # print links_confirmed_old.count()
        #
        G_standard = self.build_graph_id(links_confirmed_old)
        G_new = self.build_graph_id(links_new)
        # #
        # self.print_info(G_standard, 'standard')
        # self.print_info(G_new, 'new')

        # print sum([1.0 for s, t in G_new.edges() if G_standard.has_edge(s, t)]), G_standard.number_of_edges()
        # print sum([1.0 for s, t in G_new.edges() if G_standard.has_edge(s, t)]) / G_standard.number_of_edges()
        #

        # groups
        # cf = csv.reader(file('D:\master\LineMe\student list/grouping.csv', 'rb'))
        # # cf = csv.reader(file(BASE_DIR + '/static/data/grouping.csv', 'rb'))
        #
        # self.groups, members = {}, []
        # i = 0
        # for line in cf:
        #     if line[0] == '1':
        #         self.groups[i] = members
        #         i += 1
        #         members = [line[2].strip().decode('utf-8')]
        #
        #     else:
        #         members.append(line[2].strip().decode('utf-8'))
        # self.groups[i] = members
        # del self.groups[0]
        #
        # for k, v in self.groups.items():
        #     # print k, ': ', ' '.join(v)
        #
        #     new_list = []
        #
        #     for name in v:
        #         try:
        #             new_list.append(self.members.get(member_name=name))
        #         except Exception, e:
        #             new_list.append(self.members.filter(member_name=name, is_joined=True)[0])
        #
        #     self.groups[k] = new_list
        #
        # print 'total groups: ', len(self.groups)
        #
        # end = 58
        # end = 12

        # nc, np = 0, 0
        # for j in range(100):
        #     random_group = {k: random.random() for k, v in self.groups.items()}
        #     for i in range(1, end):
        #         print 'i = ', i
        #         c, p = self.crowdsourcing(sorted(random_group, key=random_group.get, reverse=True), G_standard, links, i)
        #         if i == 10:
        #             nc += c
        #             np += p
        #
        #
        #     print '=========='
        # print nc / 100.0, np / 100.0

        # group_degree = {k: sum([G_standard.degree(m.id) for m in v]) / float(len(v)) for k, v in self.groups.items()}
        # sorted_group_degree = self.sort_dict_and_print(group_degree)
        # for i in range(1, end):
        #     print 'i = ', i
        #     c, p = self.crowdsourcing(sorted_group_degree, G_standard, links, i)
        #
        # print '=========='
        #
        # betweenness = nx.betweenness_centrality(G_standard)
        # sorted_group_betweenness = sorted({k: sum([betweenness[m.id] for m in v]) for k, v in self.groups.items()}, reverse=True)
        # for i in range(1, end):
        #     print 'i = ', i
        #     c, p = self.crowdsourcing(sorted_group_betweenness, G_standard, links, i)
        #
        # print '=========='
        #
        # # #############################################################################
        # #
        #
        # group_link_count = {}
        # for k, v in self.groups.items():
        #     count = sum([links.filter(creator=m.user).count() for m in v])
        #     group_link_count[k] = count
        # #
        # sorted_group_link_count = self.sort_dict_and_print(group_link_count)
        #
        # for i in range(1, end):
        #     print 'i = ', i
        #     c, p = self.crowdsourcing(sorted_group_link_count, G_standard, links, i)
        #
        # print '=========='
        # #
        # # #############################################################################
        # #
        # # group_new_link_count = {}
        # # for k, v in self.groups.items():
        # #     count = sum([links_new.filter(creator=m.user).count() for m in v])
        # #     group_new_link_count[k] = count
        # #
        # # sorted_group_new_link_count = self.sort_dict_and_print(group_new_link_count)
        # #
        # # for i in range(1, end):
        # #     print 'i = ', i
        # #     self.crowdsourcing(sorted_group_new_link_count, G_standard, links, i)
        # # print '=========='
        # #
        # # #############################################################################
        # #
        #
        # group_accuracy, group_cover = {}, {}
        # for k, v in self.groups.items():
        #
        #     G_this_group = self.link_join(v, links, G_standard)
        #     if G_this_group.number_of_edges() == 0:
        #         group_accuracy[k], group_cover[k] = 0, 0
        #         continue
        #     else:
        #         true_count = len([1 for s, t, d in G_this_group.edges(data=True) if d['status']])
        #         group_accuracy[k], group_cover[k] = \
        #             true_count / float(G_this_group.number_of_edges()), \
        #             true_count / float(G_standard.number_of_edges())
        #
        # sorted_group_accuracy = self.sort_dict_and_print(group_accuracy, [group_link_count, group_cover])
        # for i in range(1, end):
        #     print 'i = ', i
        #     c, p = self.crowdsourcing(sorted_group_accuracy, G_standard, links, i)
        #
        # print '=========='
        #
        # # sorted_group_accuracy = self.sort_dict_and_print(group_cover, [group_link_count, group_cover])
        # # for i in range(1, end):
        # #     print 'i = ', i
        # #     c, p = self.crowdsourcing(sorted_group_accuracy, G_standard, links, i)
        # #
        # # print '=========='
        #
        # sorted_group_accuracy = self.sort_dict_and_print({k: group_accuracy[k]*group_cover[k]
        #                                                   for k, v in self.groups.items()})
        # for i in range(1, end):
        #     print 'i = ', i
        #     c, p = self.crowdsourcing(sorted_group_accuracy, G_standard, links, i)
        #
        # print '=========='
        #
        # # sorted_group_accuracy = self.sort_dict_and_print({k: group_accuracy[k]*group_cover[k]*math.log((group_degree[k] + 10) / 10.0)
        # #                                                   for k, v in self.groups.items()},
        # #                                                  [group_link_count, group_cover, group_accuracy, group_degree])
        # # for i in range(1, end):
        # #     print 'i = ', i
        # #     c, p = self.crowdsourcing(sorted_group_accuracy, G_standard, links, i)
        # #
        # # print '=========='
        #
        # sorted_group_accuracy = self.sort_dict_and_print({k: group_accuracy[k]+group_cover[k]
        #                                                   for k, v in self.groups.items()},
        #                                                  [group_link_count, group_cover, group_accuracy, group_degree])
        # for i in range(1, end):
        #     print 'i = ', i
        #     c, p = self.crowdsourcing(sorted_group_accuracy, G_standard, links, i)
        #
        # print '=========='

        # self.result_recorder(self.y, end)
        #
        G_wrong = G_new.copy()
        for s, t in G_wrong.edges():
            if G_standard.has_edge(s, t):
                G_wrong.remove_edge(s, t)
        #
        G_wrong.remove_node(10026)

        print sum([self.embeddedness(G_all_confirmed, s, t) for s, t in G_wrong.edges()]) / float(G_wrong.number_of_edges())

        #
        # a, b, c = 0, 0, 0
        #
        # print G_wrong.number_of_edges(), G_standard.number_of_edges(), G_all_confirmed.number_of_edges()
        # for s, t in G_wrong.edges():
        #     if not G_all_confirmed.has_edge(s, t):
        #         a += 1
        #     else:
        #         b += 1
        #         if G_standard.has_edge(s, t):
        #             c += 1
        #
        # print a, b, c
        #
        # self.print_info(G_wrong, 'wrong')
        #
        # print sum([len(list(nx.common_neighbors(G_standard, s, t))) / float(len(set(G_standard.neighbors(s)) | set(G_standard.neighbors(t)))) for s, t in G_wrong.edges()]) / float(G_wrong.number_of_edges())
        #

        # max_weight = max([d['weight'] for s, t, d in G_wrong.edges(data=True)])
        # print max_weight



        # m, n = 0, 0
        # for s, t, d in G_wrong.edges(data=True):
        #     if d['weight'] > 5:
        #         m += 1
        #         print s, t, d['weight']
        #         print GroupMember.objects.get(id=s).member_name, GroupMember.objects.get(id=t).member_name, str(G_all_confirmed.has_edge(s, t))
        #         if G_all_confirmed.has_edge(s, t):
        #             n += 1
        #
        # print m, n

        # mm, nn = [], []
        # for i in xrange(max_weight):
        #
        #     m, n = 0, 0
        #     for s, t, d in G_wrong.edges(data=True):
        #         if d['weight'] > i:
        #             m += 1
        #             # print s, t, d['weight']
        #             # print GroupMember.objects.get(id=s).member_name, GroupMember.objects.get(id=t).member_name, str(G_all_confirmed.has_edge(s, t))
        #             if G_all_confirmed.has_edge(s, t):
        #                 n += 1
        #
        #     print m, n
        #
        #     mm.append(m)
        #     nn.append(n)
        #
        # print mm, nn
        #
        # cliques = []
        # for clique in list(nx.find_cliques(G_wrong)):
        #     if set(clique) not in cliques:
        #         cliques.append(set(clique))
        #
        # cnt = Counter([len(c) for c in cliques])
        # print [[k, v / float(G_wrong.number_of_edges())] for k, v in cnt.items()]
        #
        # print len(cliques)

        # cnt = Counter([len(c) for c in cliques])
        # print cnt

        # cnt = Counter()
        # for s, t in G_wrong.edges():
        #     print s, t
        #
        #     for c in cliques:
        #         if s in c:
        #             tc = c
        #             sub = G_standard.subgraph(tc.add(t))
        #             if not nx.is_connected(sub):
        #                 print 'hi'
        #             cnt[(s, t)] += 1
        #
        #         elif t in c:
        #             tc = c
        #             sub = G_standard.subgraph(tc.add(s))
        #             if not nx.is_connected(sub):
        #                 print 'hi'
        #
        #             cnt[(s, t)] += 1
        #
        #     # print cnt
        #
        # print sorted(cnt, key=cnt.get, reverse=True)[0]

        # for clique in sorted(cliques, key=lambda x: len(x), reverse=True):
        #     print ' '.join([GroupMember.objects.get(id=node).member_name for node in clique])
        #
        # print ''
        # cliques = []
        # for clique in list(nx.find_cliques(G_wrong)):
        #     cliques.append(G_wrong.subgraph(clique))
        #
        # for clique in sorted(cliques, key=lambda x: x.number_of_nodes(), reverse=True):
        #     print ' '.join([GroupMember.objects.get(id=node).member_name for node in clique])
        #
        #
        # cnt = Counter()
        # c = 0
        # for s, t, d in G_wrong.edges(data=True):
        #     cnt[d['weight']] += 1
        #     # if d['weight'] > 6:
        #     #     print d['link'][0], d['weight']
        #     c += len(list(nx.common_neighbors(G_standard, s, t))) / float(len(set(G_standard.neighbors(s)) | set(G_standard.neighbors(t))))
        # print cnt
        # print c / G_wrong.number_of_edges()
        #
        # cnt = Counter()
        # c = 0
        # for s, t, d in G_standard.edges(data=True):
        #     cnt[d['weight']] += 1
        #     # if d['weight'] > 6:
        #     #     print d['link'][0], d['weight']
        #     embed = len(list(nx.common_neighbors(G_standard, s, t))) / float(len(set(G_standard.neighbors(s)) | set(G_standard.neighbors(t))))
        #     c += embed
        #     # print embed
        # print cnt
        # print c / G_standard.number_of_edges()
        #
        #
        # for m in sorted(G_standard.degree(), key=G_standard.degree().get, reverse=True)[:10]:
        #     print GroupMember.objects.get(id=m).member_name, G_standard.degree(m)
        #
        # print ''
        # #
        # s, w = [], []
        # for m in sorted(G_wrong.degree(), key=G_wrong.degree().get, reverse=True):
        #     print GroupMember.objects.get(id=m).member_name, G_standard.degree(m), G_wrong.degree(m)
        #     s.append(G_standard.degree(m))
        #     w.append(G_wrong.degree(m))
        #
        # print s, w


        # not recovered
        G_recovered = G_standard.copy()
        G_not_recovered = G_standard.copy()
        for s, t in G_new.edges():
            if G_not_recovered.has_edge(s, t):
                G_not_recovered.remove_edge(s, t)

        for s, t in G_not_recovered.edges():
            G_recovered.remove_edge(s, t)

        print sum([self.embeddedness(G_all_confirmed, s, t) for s, t in G_recovered.edges()]) / float(G_recovered.number_of_edges())
        print sum([self.embeddedness(G_all_confirmed, s, t) for s, t in G_not_recovered.edges()]) / float(G_not_recovered.number_of_edges())

        #
        for s, t, d in G_standard.edges(data=True):
            if not G_standard.has_edge(s, t):
                if d['ks'] > 0:
                    print s, t, d['weight']
        #
        # clique_index = {}
        # for i, c in enumerate(c_15):
        #     for m in c:
        #         if m in clique_index:
        #             clique_index[m].add(i)
        #         else:
        #             clique_index[m] = {i}
        #
        # for s, t in G_not_recovered.edges():
        #     if s not in clique_index or t not in clique_index:
        #         print s, t
        #         continue
        #     cs, ts = clique_index[s], clique_index[t]
        #     print s, t, cs, ts


        #
        # print G_not_recovered.number_of_edges()
        #
        # cnt = Counter()
        # for s, t, d in G_not_recovered.edges(data=True):
        #     cnt[d['weight']] += 1
        #
        # print cnt
        # #
        # print 1 - G_not_recovered.number_of_edges() / float(G_standard.number_of_edges())
        #
        # print [[k, v / float(G_not_recovered.number_of_nodes())] for k, v in Counter(G_not_recovered.degree().values()).items()]
        # print sum([len(list(nx.common_neighbors(G_standard, s, t))) / float(len(set(G_standard.neighbors(s)) | set(G_standard.neighbors(t)))) for s, t in G_recovered.edges()]) / float(G_recovered.number_of_edges())
        # print sum([len(list(nx.common_neighbors(G_standard, s, t))) / float(len(set(G_standard.neighbors(s)) | set(G_standard.neighbors(t)))) for s, t in G_not_recovered.edges()]) / float(G_not_recovered.number_of_edges())
        #
        # private_member = set([])
        # clear_member = set([])
        # c, my, his = 0, 0, 0
        # for node in G_not_recovered.nodes():
        #     if G_not_recovered.degree(node) > 5:
        #         private_member.add(node)
        #         for neighbor in G_not_recovered.neighbors(node):
        #             for link in self.before_time(links_confirmed, self.horizon).filter(Q(source_member__id=node, target_member__id=neighbor) | Q(source_member__id=neighbor, target_member__id=node)):
        #                 # print str(link), GroupMember.objects.get(id=node).member_name
        #                 c += 1
        #                 if link.source_member_id == node:
        #                     if link.target_member.user == link.creator:
        #                         his += 1
        #                     elif link.source_member.user == link.creator:
        #                         my += 1
        #
        #                 elif link.target_member_id == node:
        #                     if link.target_member.user == link.creator:
        #                         my += 1
        #                     elif link.source_member.user == link.creator:
        #                         his += 1
        #     elif G_not_recovered.degree(node) == 0:
        #         clear_member.add(node)
        # print c, my, his
        #
        # c, n = 0, 0.0
        # for m in private_member:
        #     c += 1
        #     if 30 < G_standard.degree(m) < 50:
        #         n += 1
        #     print GroupMember.objects.get(id=m), G_standard.degree(m), G_not_recovered.degree(m)
        #     print ' '.join([GroupMember.objects.get(id=nei).member_name for nei in G_not_recovered.neighbors(m)])
        #
        #
        # print n / c, c, n
        #
        # print [G_standard.degree(n) for n in clear_member]
        # for n in clear_member:
        #     print GroupMember.objects.get(id=n)


        # G_comm = G_all_confirmed.copy()
        # for s, t, d in G_comm.edges(data=True):
        #     if d['ks'] < 3:
        #         G_comm.remove_edge(s, t)
        #
        # comms = list(nx.k_clique_communities(G_comm, 9))
        #
        # print len(comms), self.modularity(G_comm, comms)
        #
        # for s, t in G_not_recovered.edges():
        #     for comm in comms:
        #         if {s, t}

        #############################################################################
        #############################################################################
        #############################################################################



        #
        # group_average_degree_index = {}
        # for k, v in groups.items():
        #     group_average_degree_index[k] = sum([G_all_confirmed.degree(m) for m in v])
        #
        # # print group_average_degree_index
        #
        # for top in sorted(group_average_degree_index, key=group_average_degree_index.get, reverse=True)[:3]:
        #     print ' '.join([m.member_name for m in groups[top]])
        #     print [G_all_confirmed.degree(m) for m in groups[top]]
        #
        # group_index = {m: k for k, v in groups.items() for m in v}
        #
        # G_group = nx.Graph()
        #
        # for k, v in groups.items():
        #     G_group.add_node(k)
        #
        # for s, t in G_all_confirmed.edges():
        #     # print s.member_name, t.member_name
        #     s, t = group_index[s], group_index[t]
        #     if not G_group.has_edge(s, t):
        #         G_group.add_edge(s, t, weight=1)
        #     else:
        #         G_group[s][t]['weight'] += 1
        #
        # cnt = Counter()
        # for s, t, d in G_group.edges(data=True):
        #     # print s, t, d['weight']
        #     cnt[d['weight']] += 1
        #     # if d['weight'] < len(groups[s]) * len(groups[t]) / 2.0:
        #     #     G_group.remove_edge(s, t)
        # print cnt
        #
        # # print sum([k*v for k, v in cnt.items()])
        # print G_all_confirmed.number_of_edges() / float(G_group.number_of_edges())
        #
        # cnt = Counter(G_group.degree().values())
        # print len(self.members) / float(len(groups))
        #
        # print cnt
        # self.print_info(G_group, 'group')

        # single node
        # s, n, u, z, o = 0, 0, 0, 0, 0
        # for m in G_all_confirmed.nodes():
        #     if G_all_confirmed.degree(m) == 0:
        #         s += 1
        #         if m.user is None:
        #             n += 1
        #             print m.member_name, 'not in'
        #
        #         elif not links.filter(creator=m.user).exists():
        #             z += 1
        #             print get_user_name(m.user), 'no link create'
        #
        #         elif not links.filter((Q(source_member=m) | Q(target_member=m))).exists():
        #             u += 1
        #
        #         else:
        #             print get_user_name(m.user)
        #             t = links.filter(creator=m.user)
        #             for a in t:
        #                 print a.status, a.source_member.member_name, a.target_member.member_name
        #             o += 1
        #
        # print 'single: ', s, 'not in: ', n, 'no link: ', z, 'no invite: ', u, 'other: ', o


        # user confirmed links count
        # d = {i * 10: 0 for i in xrange(11)}
        # for m in self.members:
        #
        #     m_links = links.filter(Q(source_member=m) | Q(target_member=m)).exclude(creator=m.user)
        #     if m_links.count() == 0:
        #         r = 0
        #     else:
        #         r = m_links.filter(status=3).count() / float(m_links.count())
        #     # print r, int(r*100)/10*10
        #     # if r < 0.4:
        #     #     print m.member_name, r, m_links.count(), G_all_confirmed.degree(m)
        #     d[int(r*100)/10*10] += 1
        #
        # print 'User confirmed links'
        # print d
        #
        # # embed
        # c, cs, csc = 0, set(), {}
        #
        # for m1 in self.members:
        #     mc = 0
        #     for m2 in self.members:
        #         if m1 != m2 and G_all_confirmed.has_node(m1) and G_all_confirmed.has_node(m2):
        #             n1 = G_all_confirmed.neighbors(m1)
        #             n2 = G_all_confirmed.neighbors(m2)
        #
        #             same = len(filter(lambda x: x in n1, [n for n in n2]))
        #             r = same / float(len(n1))
        #
        #             if r > 0.8:
        #                 c += 1
        #                 mc += 1
        #
        #             cs.add(m1)
        #             cs.add(m2)
        #     csc[m1] = mc
        #
        # # print c, cs, len(cs)
        # # average user similar friend embed
        # print sum(csc.values()) / float(len(csc)), len(csc), sum(csc.values()), c
        #
        # self.print_info(G_all_confirmed, 'all confirmed')
        #
        # G_core = nx.Graph()
        #
        # wc = Counter()
        # bi, nb = 0.0, 0.0
        # for (s, t, d) in G_all_confirmed.edges(data=True):
        #     w = d['weight']
        #
        #     wc[w] += 1
        #
        #     if w > 1:
        #         # print s.member_name, t.member_name
        #
        #         links = d['link']
        #         couple = {s.user: False, t.user: False}
        #
        #         for link in links:
        #             if link.creator in couple:
        #                 couple[link.creator] = True
        #
        #         if couple.values() == [True, True]:
        #             G_core.add_edge(s, t)
        #             bi += 1
        #         else:
        #             nb += 1
        #             # for link in links:
        #             #     print link.source_member.member_name, link.target_member.member_name, get_user_name(link.creator), link.status, d['weight']
        #             #
        #             # print '======'
        #
        # print 'weight distribution: ', wc, bi, nb
        #
        # self.print_info(G_core, 'global core')
        # self.connected_component(G_core)
        #
        # G_no_hub = copy.deepcopy(G_all_confirmed)
        #
        # for node in G_no_hub.nodes():
        #     if G_no_hub.degree(node) > 50:
        #         # for n in G_all_confirmed.neighbors(node):
        #         #     G_center.add_edge(node, n)
        #         G_no_hub.remove_node(node)
        #
        # self.print_info(G_no_hub, 'no hub')
        # self.connected_component(G_no_hub)
        #
        # G_only_hub = copy.deepcopy(G_all_confirmed)
        #
        # for s, t in G_only_hub.edges():
        #     if G_only_hub.degree(s) < 50 and G_only_hub.degree(t) < 50:
        #         G_only_hub.remove_edge(s, t)
        #
        # self.print_info(G_only_hub, 'only hub')
        # self.connected_component(G_only_hub)

        # top5 = sorted(G_all_confirmed.degree().items(), key=lambda x: x[1], reverse=True)[0:5]
        # p = nx.shortest_path(G_all_confirmed)
        #
        # c = 0.0
        # for m1 in self.members:
        #     for m2 in self.members:
        #         if m1 != m2 and G_all_confirmed.has_node(m1) and G_all_confirmed.has_node(m2):
        #             for t, v in top5:
        #                 if t in p[m1][m2]:
        #                     c += 1
        #                     # print p[m1][m2]
        #                     continue
        # p = nx.shortest_path(G_all_confirmed, source=m1, target=m2)
        # print p

        # print 'shortest path through: '
        # print c / len(self.members) ** 2
        #
        # self.print_info(G_all_unconfirmed, 'unconfirmed')
        # self.connected_component(G_all_unconfirmed)
        #
        # c, u, o, y = 0.0, 0.0, 0.0, 0.0
        # for (s, t, d) in G_all_unconfirmed.edges(data=True):
        #
        #     links = d['link']
        #
        #     if G_all_confirmed.has_edge(s, t):
        #         c += 1
        #
        #     elif len(links) == 1:
        #         if links[0].source_member.user is None or links[0].target_member.user is None:
        #             u += 1
        #
        #         else:
        #             o += 1
        #
        #     else:
        #         # for link in links:
        #         #     print link.source_member.member_name, link.target_member.member_name, get_user_name(link.creator), link.status
        #         couple = {s.user: False, t.user: False}
        #
        #         for link in links:
        #             if link.creator in couple:
        #                 # print couple, link.creator
        #                 couple[link.creator] = True
        #
        #         if couple.values() == [True, True]:
        #             y += 1
        #         # print '+++++'
        #
        #
        # print 'ratio: ', c / G_all_unconfirmed.number_of_edges(), \
        #     u / G_all_unconfirmed.number_of_edges(), \
        #     o / G_all_unconfirmed.number_of_edges(), c, u, o, y

        # G_active, G_passive = nx.Graph(), nx.Graph()
        #
        # for m in self.members:
        #     if m.user is not None:
        #         my_links = links_confirmed.filter((Q(source_member=m) | Q(target_member=m)))
        #         active_links = my_links.filter(creator=m.user)
        #         passive_links = my_links.exclude(creator=m.user)
        #         c1 = active_links.count()
        #         c2 = passive_links.count()
        #         if c1 != 0 and c2 != 0:
        #             print get_user_name(m.user), \
        #                 active_links.count(), \
        #                 passive_links.count(), (c1-c2)/float(c1+c2)

    def build_graph(self, links):
        G = nx.Graph()
        for m in self.members:
            G.add_node(m)

        for link in links:
            s, t = self.members.get(id=link.source_member_id), self.members.get(id=link.target_member_id)
            if not G.has_edge(s, t):
                G.add_edge(s, t, link=[link], weight=1, ks=0)
            else:
                G[s][t]['weight'] += 1
                G[s][t]['link'].append(link)

            su, tu = link.source_member.user.id, link.target_member.user.id
            if link.creator_id == su or link.creator_id == tu:
                pass
            else:
                G[s][t]['ks'] += 1

        return G

    def build_graph_id(self, links):
        G = nx.Graph()
        for m in self.members:
            G.add_node(m.id)

        for link in links:
            s, t = link.source_member_id, link.target_member_id
            if not G.has_edge(s, t):
                G.add_edge(s, t, link=[link], weight=1, ks=0)
            else:
                G[s][t]['weight'] += 1
                G[s][t]['link'].append(link)

            su, tu = self.member_user_index[s], self.member_user_index[t]
            if link.creator_id == su or link.creator_id == tu:
                pass
            else:
                G[s][t]['ks'] += 1
        return G

    def confirmed(self, links):
        return links.filter(status=3)

    def unconfirmed(self, links):
        return links.exclude(status=3)

    def unconfirmed_not_reject(self, links):
        return links.filter(status__gte=0)

    def single_rejected(self, links):
        return links.filter(status__lt=0).exclude(status=-3)

    def both_rejected(self, links):
        return links.filter(status=-3)

    def before_time(self, links, timestamp):
        return links.filter(created_time__lt=timestamp)

    def after_time(self, links, timestamp):
        return links.filter(created_time__gt=timestamp)

    def print_info(self, G, name):
        print name
        print 'nodes: ', G.number_of_nodes(), ' links: ', G.number_of_edges()
        print 'average degree: ', self.average_degree(G), 'average_shortest_path: ', self.average_shortest_path_length(
            G)

    def sort_dict_and_print(self, d, args=list(), p=True):
        std = sorted(d, key=d.get, reverse=True)
        if p:
            for i, g in enumerate(std):
                print i, ' ', ' '.join([m.member_name for m in self.groups[g]]), d[g],
                for arg in args:
                    print arg[g],
                print ''
        return std

    def result_recorder(self, y, end):
        with open('result.txt', 'w') as f:
            c, p = [], []
            f.write('[')
            for i, n in enumerate(y):

                if i % (end-1) == 0 and i != 0:
                    f.write(str(c)+',\n')
                    f.write(str(p)+',\n')

                    c, p = [], []
                c.append(n[0])
                p.append(n[1])
            f.write(str(c)+',\n')
            f.write(str(p)+',\n')
            f.write(']')

    def average_degree(self, G):
        return 2.0 * G.number_of_edges() / G.number_of_nodes()

    def average_shortest_path_length(self, G):
        # for g in nx.connected_component_subgraphs(G):
        #     for n in g.nodes():
        #         print n.member_name
        #     print '=='
        d = [nx.average_shortest_path_length(g) for g in nx.connected_component_subgraphs(G) if g.number_of_nodes() > 1]
        print '(', len(d), 'component)',
        return sum(d) / len(d)

    def connected_component(self, G):
        for g in nx.connected_component_subgraphs(G):
            if g.number_of_nodes() != 1:
                print g.number_of_nodes(), g.number_of_edges()

    def link_join(self, group, links, G_standard):
        G_this_group = nx.Graph()
        for m in group:
            for link in links.filter(creator=m.user):
                s, t = link.source_member_id, link.target_member_id
                if G_standard.has_edge(s, t):
                    G_this_group.add_edge(s, t, status=True)
                else:
                    G_this_group.add_edge(s, t, status=False)

        return G_this_group

    def crowdsourcing(self, sorted_groups, G_standard, links, top):
        G_best = nx.Graph()
        for best in sorted_groups[:top]:
            for m in self.groups[best]:
                for link in links.filter(creator=m.user):
                    s, t = link.source_member_id, link.target_member_id
                    if G_standard.has_edge(s, t):
                        G_best.add_edge(s, t, status=True)
                    else:
                        G_best.add_edge(s, t, status=False)

        G_before = nx.Graph()
        for before in sorted_groups[:top]:
            for m in self.groups[before]:
                for link in links.filter(creator=m.user, created_time__lt=self.horizon, status=3):
                    s, t = link.source_member_id, link.target_member_id

                    G_before.add_edge(s, t, status=True)

        correct = sum([1.0 for (s, t, d) in G_best.edges(data=True) if d['status']])
        c, p = correct / G_standard.number_of_edges(), correct / G_best.number_of_edges()
        print 'cover ratio: ', c
        print 'correct ratio: ', p
        print G_before.number_of_edges() / float(G_standard.number_of_edges())
        self.y.append((c, p))
        return c, p

    def embeddedness(self, G, a, b):

        my_friends = set(G.neighbors(a))
        your_friends = set(G.neighbors(b))
        # my_friends.add(a)
        # your_friends.add(b)

        embeddedness = len(your_friends & my_friends) / float(len(your_friends | my_friends))

        return embeddedness

    def modularity(self, G, communities, weight='weight'):

        multigraph = G.is_multigraph()
        directed = G.is_directed()
        m = G.size(weight=weight)
        if directed:
            out_degree = dict(G.out_degree(weight=weight))
            in_degree = dict(G.in_degree(weight=weight))
            norm = 1 / m
        else:
            out_degree = dict(G.degree(weight=weight))
            in_degree = out_degree
            norm = 1 / (2 * m)

        def val(u, v):
            try:
                if multigraph:
                    w = sum(d.get(weight, 1) for k, d in G[u][v].items())
                else:
                    w = G[u][v].get(weight, 1)
            except KeyError:
                w = 0
            # Double count self-loops if the graph is undirected.
            if u == v and not directed:
                w *= 2
            return w - in_degree[u] * out_degree[v] * norm

        Q = sum(val(u, v) for c in communities for u, v in product(c, repeat=2))
        return Q * norm

    def variance(self, seq):
        average = sum(seq) / float(len(seq))
        var = sum([abs(average-s) ** 2 for s in seq]) / float(len(seq))
        return var




        # def find_bilink(self, links, link):
        #     creator = link.creator
        #     s_u = link.source_member.user
        #     t_u = link.target_member.user
        #
        #     if s_u == creator:
        #         red = links.filter((Q(source_member=link.source_member, target_member=link.target_member) |
        #                             Q(source_member=link.target_member, target_member=link.source_member)),
        #                            creator=t_u).exclude(id=link.id)
        #     elif t_u == creator:
        #         red = links.filter((Q(source_member=link.source_member, target_member=link.target_member) |
        #                             Q(source_member=link.target_member, target_member=link.source_member)),
        #                            creator=s_u).exclude(id=link.id)
        #
        #     return red

        # def link_created_count_interval(self, f, t):
        #     return



        #
        # a, b, c = 0, 0, 0
        # for link in links:
        #     # simi = links.filter((Q(source_member=link.source_member, target_member=link.target_member) |
        #     #                     Q(source_member=link.target_member, target_member=link.source_member))).exclude(id=link.id)
        #     # if simi.exists():
        #     #
        #     #     s = simi.filter(Q(creator=link.target_member.user) | Q(creator=link.source_member.user))[0]
        #     #
        #     #     # print link.creator
        #     #     if link.status == 3 and s.status != 3:
        #     #         # print link.source_member.member_name, link.target_member.member_name, s.source_member.member_name, s.target_member.member_name
        #     #         a += 1
        #     #
        #     #     if (link.status == 2 and s.status == 1) or (link.status == 1 and s.status == 2):
        #     #         print link.source_member.member_name, link.target_member.member_name, s.source_member.member_name, s.target_member.member_name
        #     #         b += 1
        #
        #     if self.find_bilink(links, link).exists():
        #         bi = self.find_bilink(links, link)[0]
        #
        #         if link.status == 3 and bi.status != 3:
        #             # print link.source_member.member_name, link.target_member.member_name, s.source_member.member_name, s.target_member.member_name
        #             a += 1
        #
        #         if (link.status == 2 and bi.status == 1) or (link.status == 1 and bi.status == 2):
        #             print link.source_member.member_name, link.target_member.member_name, bi.source_member.member_name, bi.target_member.member_name
        #             print link.creator, bi.creator
        #             b += 1
        #
        # print a, 'double link both unconfirmed: ', b
        #
        # G_no_hub = copy.deepcopy(G_all_confirmed)
        # for node in G_no_hub.nodes():
        #     if G_no_hub.degree(node) > 50:
        #         # for n in G_all_confirmed.neighbors(node):
        #         #     G_center.add_edge(node, n)
        #         G_no_hub.remove_node(node)
        #
        # self.print_info(G_no_hub, 'no hub')
        # print 'component'
        # self.connected_component(G_no_hub)
        #
        # G_only_hub = copy.deepcopy(G_all_unconfirmed)
        #
        # for s, t in G_only_hub.edges():
        #     if G_only_hub.degree(s) < 50 and G_only_hub.degree(t) < 50:
        #         G_only_hub.remove_edge(s, t)
        #
        # self.print_info(G_no_hub, 'only hub')
        # print 'component'
        # self.connected_component(G_only_hub)




        # for (s, t, d) in G_all_unconfirmed.edges(data=True):
        #     if d['weight'] > 1:
        #         print s.member_name, t.member_name





        ######################################################################################

        # dis = {}
        # for s, t, d in G_all_unconfirmed.edges(data=True):
        #     w = d['weight']
        #     if w in dis:
        #         dis[w] += 1
        #     else:
        #         dis[w] = 1
        #
        #     if w > 1:
        #         # print s.member_name, t.member_name, d['link'].creator
        #         ls = links_unconfirmed.filter(Q(source_member=s, target_member=t)|Q(source_member=t,target_member=s))
        #         for l in ls:
        #             print l.id, l.source_member.user, l.target_member.user, l.creator
        # print dis
        # d = datetime.timedelta()
        # for link in links_confirmed:
        #     # print link.confirmed_time - link.created_time
        #     d += link.confirmed_time - link.created_time
        #
        # print d / links_confirmed.count()
        #
        # t = {}
        # for m in self.members:
        #     links = links_confirmed.filter(creator=m.user)
        #     if links.exists():
        #         d = datetime.timedelta()
        #         for link in links:
        #             d += link.confirmed_time - link.created_time
        #
        #         t[m] = d / links.count()
        #
        # st = sorted(t, key=t.get)
        # for s in st[:100]:
        #     if G_all_confirmed.has_node(s):
        #         print G_all_confirmed.degree(s), s.member_name, t[s]

        # top5 = sorted(G_all_confirmed.degree().items(), key=lambda x: x[1], reverse=True)[0:5]
        # print top5
        #
        # p = nx.shortest_path(G_all_confirmed)
        # # print p
        # c = 0.0
        # for m1 in self.members:
        #     for m2 in self.members:
        #         if m1 != m2 and G_all_confirmed.has_node(m1) and G_all_confirmed.has_node(m2):
        #             for t, v in top5:
        #                 if t in p[m1][m2]:
        #                     c += 1
        #                     # print p[m1][m2]
        #                     continue
        #         # p = nx.shortest_path(G_all_confirmed, source=m1, target=m2)
        #         # print p
        #
        # print c / len(self.members) ** 2

        # c, cs, csc = 0, set(), {}
        #
        # for m1 in self.members:
        #     mc = 0
        #     for m2 in self.members:
        #         if m1 != m2 and G_all_confirmed.has_node(m1) and G_all_confirmed.has_node(m2):
        #             n1 = G_all_confirmed.neighbors(m1)
        #             n2 = G_all_confirmed.neighbors(m2)
        #
        #             same = len(filter(lambda x: x in n1, [n for n in n2]))
        #             r = same / float(len(n1))
        #
        #             if r > 0.8:
        #                 c += 1
        #                 mc += 1
        #
        #             cs.add(m1)
        #             cs.add(m2)
        #     csc[m1] = mc
        #
        # print c, cs, len(cs)
        # print sum(csc.values()) / len(csc), len(csc), sum(csc.values())

        # close = nx.closeness_vitality(G_all_confirmed)
        # for k, v in sorted(close.items(), key=operator.itemgetter(1), reverse=True):
        #     print k.member_name, v

        # day = datetime.datetime(2016, 9, 26)
        #
        # print links_confirmed.filter(confirmed_time__gt=datetime.datetime(2016,9,27,10), confirmed_time__lt=datetime.datetime(2016,9,27,12)).count()
        # x = []
        # n, l, d, dis = [], [], [], []
        # for i in xrange(7*12):
        #
        #     day += datetime.timedelta(hours=2)
        #
        #     x.append(day)
        #     G_time = self.build_graph(links_confirmed.filter(confirmed_time__lt=day))
        #     dt = self.average_shortest_path_length(G_time)
        #     # n.append(G_time.number_of_nodes())
        #     # l.append(G_time.number_of_edges())
        #     # d.append(self.average_degree(G_time))
        #     dis.append(dt)
        #
        #     print day, dt, links_confirmed.filter(confirmed_time__lt=day).count()

        # self.print_info(G_time)
        # print 'average degree: ', self.average_degree(G_time)
        # print 'average distance: ', self.average_shortest_path_length(G_time), '\n'
        # fig1 = plt.figure('node')
        # plt.plot(x, n)
        # fig2 = plt.figure('link')
        # plt.plot(x, l)
        # fig3 = plt.figure('degree')
        # plt.plot(x, d)
        # fig4 = plt.figure('distance')
        # plt.plot(x, dis)
        #
        #
        #
        #
        # plt.show()




        # G_core, G_normal = nx.Graph(), nx.Graph()
        #
        # print '3: ', len(nx.triangles(G_all_confirmed))
        #
        # wc = {}
        # c = 0.0
        # for (s, t, d) in G_all_confirmed.edges(data=True):
        #     w = d['weight']
        #     if w in wc:
        #         wc[w] += 1
        #     else:
        #         wc[w] = 1
        #
        #     if w == 2:
        #         link = d['link']
        #         if links_confirmed.filter(Q(source_member=s, target_member=t)|Q(source_member=t,target_member=s)).exclude(id=link.id).exists():
        #             c += 1
        #
        #     if w > 1:
        #         # print s.member_name, t.member_name
        #         G_core.add_edge(s, t)
        #
        # print wc, c
        #
        # self.print_info(G_core)
        # print 'average degree: ', self.average_degree(G_core)
        # print 'average distance: ', self.average_shortest_path_length(G_core), '\n'
        #
        # ti, c = datetime.timedelta(), 0
        # for s, t in G_core.edges():
        #     links = links_confirmed.filter(Q(source_member=s, target_member=t)|Q(source_member=t,target_member=s))
        #
        #     for l in links:
        #         # print l.created_time
        #         ti += l.confirmed_time - l.created_time
        #
        #         c += 1
        #
        # print ti / c
        # m, f = 0, 0
        # for n in G_core.nodes():
        #     if n.user.extra.gender:
        #         f += 1
        #     else:
        #         m += 1
        # print m, f



        # c, u, b, f, s = 0.0, 0.0, 0.0, 0.0, 0.0
        # for (s, t, d) in G_all_unconfirmed.edges(data=True):
        #     if G_all_confirmed.has_edge(s, t):
        #         c += 1
        #
        #     # if G_friend_unconfirmed.has_edge(s, t):
        #     #     if d['link'].source_member.user is None or d['link'].target_member.user is None:
        #     #         pass
        #     #     else:
        #     #         f += 1
        #     else:
        #         if d['link'].source_member.user is None or d['link'].target_member.user is None:
        #             u += 1
        #
        #         elif G_friend_unconfirmed.has_edge(s, t):
        #             f += 1
        #             if d['link'].creator == s.user:
        #                 if links.filter(creator=t.user, source_member=t, target_member=s).exists():
        #                     l = links.filter(creator=t.user, source_member=t, target_member=s)[0]
        #                     print l.creator, l.source_member_id, l.target_member_id
        #             elif d['link'].creator == t.user:
        #                 if links.filter(creator=s.user, source_member=t, target_member=s).exists():
        #                     print s.member_name, t.member_name

        # else:
        # if Link.objects.filter()
        # print s.member_name, t.member_name, G_all.degree(s), G_all.degree(t)

        # print 'ratio: ', c / G_all_unconfirmed.number_of_edges(), c, u, f

        # print 'all'
        # self.print_info(G_all)
        # print 'average degree: ', self.average_degree(G_all)
        # print 'average distance: ', self.average_shortest_path_length(G_all), '\n'
        #
        # print 'friend'
        # self.print_info(G_friend)
        # print 'average degree: ', self.average_degree(G_friend)
        # print 'average distance: ', self.average_shortest_path_length(G_friend), '\n'
        #
        # print 'other'
        # self.print_info(G_other)
        # print 'average degree: ', self.average_degree(G_other)
        # print 'average distance: ', self.average_shortest_path_length(G_other), '\n'
        #

        # print 'all confirmed'
        # self.print_info(G_all_confirmed)
        # print 'average degree: ', self.average_degree(G_all_confirmed)
        # print 'average cluster: ', nx.average_clustering(G_all_confirmed)
        # print 'average distance: ', self.average_shortest_path_length(G_all_confirmed), '\n'
        # #
        # G_center = nx.Graph()
        # for node in G_all_confirmed.nodes():
        #     if G_all_confirmed.degree(node) > 80:
        #         # for n in G_all_confirmed.neighbors(node):
        #         #     G_center.add_edge(node, n)
        #         G_all_confirmed.remove_node(node)

        # print 'all confirmed'
        # self.print_info(G_center)
        # print 'average degree: ', self.average_degree(G_center)
        # print 'average cluster: ', nx.average_clustering(G_center)
        # print 'average distance: ', self.average_shortest_path_length(G_all_confirmed), '\n'
        #
        # print 'friend confirmed'
        # self.print_info(G_friend_confirmed)
        # print 'average degree: ', self.average_degree(G_friend_confirmed)
        # print 'average distance: ', self.average_shortest_path_length(G_friend_confirmed), '\n'
        #
        # print 'other confirmed'
        # self.print_info(G_other_confirmed)
        # print 'average degree: ', self.average_degree(G_other_confirmed)
        # print 'average distance: ', self.average_shortest_path_length(G_other_confirmed), '\n'
        #
        # print 'all unconfirmed'
        # self.print_info(G_all_unconfirmed)
        # print 'average degree: ', self.average_degree(G_all_unconfirmed)
        # print 'average distance: ', self.average_shortest_path_length(G_all_unconfirmed), '\n'
        #
        # print 'friend unconfirmed'
        # self.print_info(G_friend_unconfirmed)
        # print 'average degree: ', self.average_degree(G_friend_unconfirmed)
        # print 'average distance: ', self.average_shortest_path_length(G_friend_unconfirmed), '\n'
        #
        # print 'other unconfirmed'
        # self.print_info(G_other_unconfirmed)
        # print 'average degree: ', self.average_degree(G_other_unconfirmed)
        # print 'average distance: ', self.average_shortest_path_length(G_other_unconfirmed), '\n'

        # for m in self.members:
        #     if m is not None:
        #         G = Graph(m.user, Group.objects.get(id=10001)).ego_builder().bingo()
        #         es = links.filter(creator=m.user)
        #
        #         for e in es:
        #             if not G.has_edge(e.source_member, e.target_member):
        #                 print m.user, es.count(), G.number_of_edges()
        #                 break
        #
        #         if es.count() != G.number_of_edges():
        #             print m.user, es.count(), G.number_of_edges()
        # link = links.get(status=-3)
        # print male_count, female_count

        #         a, b, c = 0, 0, 0
        # for link in links:
        #     simi = links.filter((Q(source_member=link.source_member, target_member=link.target_member) |
        #                         Q(source_member=link.target_member, target_member=link.source_member)),
        #                         creator=link.creator).exclude(id=link.id)
        #     if simi.exists():
        #
        #         s = simi.filter(Q(creator=link.target_member.user)|Q(creator=link.source_member.user))[0]
        #
        #         # print link.creator
        #         if link.status == 3 and s.status != 3:
        #             print link.source_member.member_name, link.target_member.member_name, s.source_member.member_name, s.target_member.member_name
        #             a += 1
        #
        #         if (link.status == 2 and s.status == 1) or (link.status == 1 and s.status == 2):
        #             print link.source_member.member_name, link.target_member.member_name, s.source_member.member_name, s.target_member.member_name
        #             b += 1
        #
        # print a, b
