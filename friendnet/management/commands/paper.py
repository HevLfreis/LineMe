#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/11/28
# Time: 18:56

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
        self.member_user_index = {m.id: m.user for m in self.members}

        male_count = self.members.filter(user__extra__gender=False).count()
        female_count = self.members.filter(user__extra__gender=True).count()

        print male_count, female_count

        links = Link.objects.filter(group__id=groupid)
        print 'total links: ', links.count()

        friend_links = links.filter(Q(source_member__user=F('creator')) | Q(target_member__user=F('creator')))
        print 'friend links: ', friend_links.count()

        links_confirmed = self.confirmed(links)
        print 'total links confirmed: ', links_confirmed.count()

        links_unconfirmed = self.unconfirmed(links)
        print 'total links unconfirmed: ', links_unconfirmed.count()

        links_s_rejected = self.single_rejected(links)
        links_b_rejected = self.both_rejected(links)
        print 'single reject: ', links_s_rejected.count()
        print 'both reject: ', links_b_rejected.count(), '\n'

        self.horizon = datetime.datetime(2016, 10, 27, 10, 0, 0)
        # self.horizon = datetime.datetime(2016, 11, 29, 10, 0, 0)
        links_new = self.after_time(links, self.horizon)
        links_old = self.before_time(links, self.horizon)
        links_confirmed_old = self.before_time(links_confirmed, self.horizon)
        print 'new/old links count: ', links_new.count(), links_old.count(), '\n'
        # print links_new.filter((Q(source_member__user=F('creator')) | Q(target_member__user=F('creator')))).count()

        # print self.single_rejected(links_old).count(), self.both_rejected(links_old).count()

        G_all_confirmed = self.build_graph_id(links_confirmed)
        G_standard = self.build_graph_id(links_confirmed_old)
        G_new = self.build_graph_id(links_new)

        # self.print_info(G_all_confirmed, 'all')

        G_final = G_standard.copy()

        for s, t, d in G_new.edges(data=True):
            if G_final.has_edge(s, t):
                G_final[s][t]['ks'] += G_new[s][t]['ks']
                G_final[s][t]['weight'] += G_new[s][t]['weight']
            else:
                if s == 10026 or t == 10026 or d['ks'] == 0:
                    pass
                else:
                    G_final.add_edge(s, t, weight=-d['weight'], ks=-d['ks'])

        # print G_final.number_of_edges()
        # print sum([1.0 for s, t in G_new.edges() if G_standard.has_edge(s, t)]) / G_new.number_of_edges()

        G_double_confirmed = G_standard.copy()
        for s, t, d in G_standard.edges(data=True):
            if d['weight'] - d['ks'] != 2:
                G_double_confirmed.remove_edge(s, t)
            #     print s, t, 0 + random.random() / 2
            # else:
            #     print s, t, 1 - random.random() / 2

        G_recovered = G_standard.copy()
        G_not_recovered = G_standard.copy()
        for s, t in G_new.edges():
            if G_standard.has_edge(s, t):
                G_not_recovered.remove_edge(s, t)

        self.print_info(G_not_recovered, 'double')

        G_not_recovered_double = G_double_confirmed.copy()
        for s, t in G_new.edges():
            if G_double_confirmed.has_edge(s, t):
                G_not_recovered_double.remove_edge(s, t)

        for s, t in G_not_recovered.edges():
            G_recovered.remove_edge(s, t)

        G_wrong = G_new.copy()
        for s, t in G_wrong.edges():
            if G_standard.has_edge(s, t):
                G_wrong.remove_edge(s, t)
        G_wrong.remove_node(10026)

        # m = [10135, 10042, 10078, 10134, 10076, 10071, 10171, 10120]
        # mm = GroupMember.objects.filter(id__in=m)
        # for a in mm:
        #     print a.member_name, a.id

        # i = 0
        # for link in links_new:
        #     if G_standard.has_edge(link.source_member_id, link.target_member_id):
        #         i += 1
        # print i
        # print i / float(links_new.count())
        # cnt = Counter()
        # cnt2 = Counter()
        # for m in self.members:
        #     G_ego = self.build_graph_id(links_new.filter(creator=m.user))
        #
        #     mid = m.id
        #     for s, t in G_ego.edges():
        #         if s == mid or t == mid:
        #             cnt[0] += 1
        #         elif nx.has_path(G_standard, mid, t) and nx.has_path(G_standard, mid, s):
        #             d1, d2 = nx.shortest_path_length(G_standard, mid, s), nx.shortest_path_length(G_standard, mid, t)
        #             if d1 == d2 == 1:
        #                 cnt[1] += 1
        #             elif (d1 == 1 and d2 == 2) or (d1 == 2 and d2 == 1):
        #                 cnt[1.5] += 1
        #             elif d1 == 2 and d2 == 2:
        #                 cnt[2] += 1
        #             else:
        #                 print d1, d2, GroupMember.objects.get(id=s), G_standard.degree(s), GroupMember.objects.get(id=t), G_standard.degree(t), m.member_name
        #                 cnt[3] += 1
        #
        #                 cnt2[str({d1, d2})] += 1
        #
        #         else:
        #             cnt[-1] += 1
        # print [[k, v/float(links_new.count())] for k, v in cnt.items()]
        # print [[k, v] for k, v in cnt.items()]
        # print [[k, v] for k, v in cnt2.items()]
        # print sum([v for k, v in cnt.items()])

        # for s, t, d in G_final.edges(data=True):
        #     if d['ks'] < -9:
        #         print self.members.get(id=s), self.members.get(id=t), d['ks']

        # print Counter([nx.shortest_path_length(G_standard, s, t) for s in G_standard.nodes() for t in G_standard.nodes()])

        # cnt = Counter()
        # cnta = Counter()
        #
        # x, m, f = 0, 0, 0
        # for s, t, d in G_wrong.edges(data=True):
        #     ks = d['ks']
        #     cnta[ks] += 1
        #
        #     sm, tm = GroupMember.objects.get(id=s), GroupMember.objects.get(id=t)
        #
        #     if G_all_confirmed.has_edge(s, t):
        #         cnt[ks] += 1
        #         # print sm, tm, sm.user.extra.gender, tm.user.extra.gender
        #
        #         if sm.user.extra.gender != tm.user.extra.gender:
        #             x += 1
        #         elif sm.user.extra.gender == True == tm.user.extra.gender:
        #             f += 1
        #         else:
        #             m += 1
        #
        # print x, f, m
        # print [[k, cnt[k], v] for k, v in cnta.items()], k, G_wrong.number_of_edges()

        # print G_not_recovered.number_of_edges()
        #
        # ego, between_ego, other = 0, 0, 0
        # for m in self.members:
        #     ego_links = links.filter(creator=m.user)
        #     G_ego = self.build_graph_id(ego_links)
        #
        #     ego += len(list(G_ego.neighbors(m.id)))
        #
        #     between_ego += nx.ego_graph(G_ego, m.id).number_of_edges() - len(list(G_ego.neighbors(m.id)))
        #
        #     other += G_ego.number_of_edges() - nx.ego_graph(G_ego, m.id).number_of_edges()
        #
        # print ego, between_ego, other, ego+between_ego+other

        # print G_wrong.number_of_edges()

        max_weight = max([d['ks'] for s, t, d in G_final.edges(data=True)])
        max_weight_wrong = max([d['ks'] for s, t, d in G_wrong.edges(data=True)])

        # for n in G_standard.nodes():
        #     fs = G_standard.neighbors(n)
        #     fd = G_double_confirmed.neighbors(n)
        #
        #     print G_standard.degree(n), len(set(fs) - set(fd))

        # for s, t in G_standard.edges():
        #     print s, t

        # G_weight = G_final.copy()
        # for s, t, d in G_final.edges(data=True):
        #     if d['ks'] < 8:
        #         G_weight.remove_edge(s, t)
        #     else:
        #         print s, t, G_final[s][t]['ks']
        # print G_final[10071][10076]['ks']
        # # print max_weight, max_weight_wrong

        # for i in xrange(3, 20):
        #     c = list(nx.k_clique_communities(G_standard, i))
        #     print i, len(c), self.modularity(G_standard, c)

        #############################################################################
        # ks vs betweenness, link prediction, embed, negative corr
        betweenness = nx.edge_betweenness_centrality(G_standard)

        #
        # b = {}
        # for st in betweenness:
        #     # print r
        #     ks = G_final[st[0]][st[1]]['ks']
        #     if ks in b:
        #         b[ks].append(betweenness[st])
        #     else:
        #         b[ks] = [betweenness[st]]
        # print [[k, sum(v) / len(v), self.variance(v)] for k, v in b.items()]
        #
        # e = {}
        # for s, t in G_standard.edges():
        #     ks = G_final[s][t]['ks']
        #     if ks in e:
        #         e[ks].append(self.embeddedness(G_standard, s, t))
        #     else:
        #         e[ks] = [self.embeddedness(G_standard, s, t)]
        # print [[k, sum(v) / len(v), self.variance(v), max(v), min(v)] for k, v in e.items()]

        # e = {}
        # for s, t in G_final.edges():
        #
        #     ks = G_final[s][t]['ks']
        #     if ks < 0:
        #         if ks in e:
        #             e[ks].append(self.embeddedness(G_standard, s, t))
        #         else:
        #             e[ks] = [self.embeddedness(G_standard, s, t)]
        # # print len(e[0])
        # print [[k, sum(v) / len(v), self.variance(v), max(v), min(v)] for k, v in e.items()]

        # r = {}
        # for s, t in G_standard.edges():
        #     ks = G_final[s][t]['ks']
        #     pred = sum(1.0 / G_standard.degree(w) for w in nx.common_neighbors(G_standard, s, t))
        #     if ks in r:
        #         r[ks].append(pred)
        #     else:
        #         r[ks] = [pred]
        # print [[k, sum(v) / len(v), self.variance(v), max(v), min(v)] for k, v in r.items()]

        # #
        # r = {}
        # for s, t in G_final.edges():
        #     ks = G_final[s][t]['ks']
        #     if ks < 0:
        #         pred = sum(1.0 / G_standard.degree(w) for w in nx.common_neighbors(G_standard, s, t))
        #         if ks in r:
        #             r[ks].append(pred)
        #         else:
        #             r[ks] = [pred]
        # print [[k, sum(v) / len(v), self.variance(v), max(v), min(v)] for k, v in r.items()]

        # mod = []
        # for j in xrange(3, 16):
        #     c = list(nx.k_clique_communities(G_standard, j))
        #     m = self.modularity(G_standard, c)
        #     mod.append(m)
        #
        # k = mod.index(max(mod))
        # k = 10
        #
        # cliques = list(nx.k_clique_communities(G_standard, k))
        # print len(cliques)
        #
        # cnts = Counter()
        # cntc = Counter()
        # for s, t, d in G_final.edges(data=True):
        #     ks = d['ks']
        #     cnts[ks] += 1
        #
        #     for cq in cliques:
        #         if len({s, t} - set(cq)) == 0:
        #             cntc[ks] += 1
        #             break
        #
        # print [[k, (v - cntc[k]) / float(v)] for k, v in cnts.items()]
        # print [[k, v, cntc[k]] for k, v in cnts.items()]

        #############################################################################
        # ks vs degree and cluster
        # de = []
        # co = []
        # for i in xrange(max_weight):
        #     G_weight = G_final.copy()
        #     for s, t, d in G_final.edges(data=True):
        #         if d['ks'] < i:
        #             G_weight.remove_edge(s, t)
        #
        #     de.append(self.average_degree(G_weight))
        #     co.append(nx.average_clustering(G_weight))
        #
        # print de
        # print co

        #############################################################################
        # ks distribution
        # print self.ks_distribution(G_final)
        # print self.ks_distribution(G_wrong)

        #############################################################################
        # ks vs embed
        # e = []
        # v = []
        # #
        # for j in xrange(-max_weight_wrong, 0):
        #     print j
        #     G_weight = G_wrong.copy()
        #     for s, t, d in G_new.edges(data=True):
        #         if -d['ks'] < j and G_weight.has_edge(s, t):
        #             G_weight.remove_edge(s, t)
        #
        #     G_weight = nx.compose(G_standard, G_weight)
        #
        #     embed_list = [self.embeddedness(G_weight, s, t) for s, t in G_weight.edges()]
        #
        #     embed = sum(embed_list) / float(G_weight.number_of_edges())
        #     var = self.variance(embed_list)
        #     ma = max(embed_list)
        #     mi = min(embed_list)
        #
        #     e.append(embed)
        #     v.append(var)
        #     # de.append(self.average_degree(G_weight))
        #     print embed, var, ma, mi
        #
        # for j in xrange(0, max_weight+1):
        #     print j
        #     G_weight = G_standard.copy()
        #     for s, t, d in G_final.edges(data=True):
        #         if d['ks'] < j and G_weight.has_edge(s, t):
        #             G_weight.remove_edge(s, t)
        #
        #     embed_list = [self.embeddedness(G_weight, s, t) for s, t in G_weight.edges()]
        #
        #     embed = sum(embed_list) / float(G_weight.number_of_edges())
        #     var = self.variance(embed_list)
        #     e.append(embed)
        #     v.append(var)
        #     # de.append(self.average_degree(G_weight))
        #     print embed, var, G_weight.number_of_edges()
        #
        # print e
        # print v

        #############################################################################
        # largest component

        # def partition(lst, n):
        #     q, r = divmod(len(lst), n)
        #     indices = [q*i + min(i, r) for i in xrange(n+1)]
        #     return [lst[indices[i]:indices[i+1]] for i in xrange(n)]
        #
        # sorted_links = sorted(G_standard.edges(), key=lambda (x, y): G_final[x][y]['ks'])
        # sorted_reversed_links = sorted(G_standard.edges(), key=lambda (x, y): G_final[x][y]['ks'], reverse=True)
        #
        # c = []
        # G = G_standard.copy()
        #
        # p = partition(sorted_reversed_links, 100)
        # for j in xrange(0, 100):
        #     print j
        #     G.remove_edges_from(p[j])
        #     largest_cc = max(nx.connected_components(G), key=len)
        #     print [len(k) for k in nx.connected_components(G)]
        #     c.append(nx.subgraph(G, largest_cc).number_of_nodes() / float(G_standard.number_of_nodes()))
        #
        # print c

        # for j in xrange(0, max_weight+1):
        #     print j
        #     G_weight = G_standard.copy()
        #     for s, t, d in G_final.edges(data=True):
        #         if d['ks'] < j and G_weight.has_edge(s, t):
        #             G_weight.remove_edge(s, t)
        #
        #     largest_cc = max(nx.connected_components(G_weight), key=len)
        #     c.append(nx.subgraph(G_weight, largest_cc).number_of_edges() / float(G_standard.number_of_edges()))
        #
        # print c
        #
        # c = []
        # for j in xrange(0, max_weight+1):
        #     print j
        #     G_weight = G_standard.copy()
        #     for s, t, d in G_final.edges(data=True):
        #         if d['ks'] > j and G_weight.has_edge(s, t):
        #             G_weight.remove_edge(s, t)
        #
        #     largest_cc = max(nx.connected_components(G_weight), key=len)
        #     c.append(nx.subgraph(G_weight, largest_cc).number_of_edges() / float(G_standard.number_of_edges()))
        #
        # print c

        #############################################################################
        # clear community
        # all_module, all_strong = [], []
        # for i in xrange(0, max_weight):
        #     print i
        #     module = []
        #     l = []
        #
        #     G_weight = G_final.copy()
        #     for s, t, d in G_final.edges(data=True):
        #         if d['ks'] < i:
        #             G_weight.remove_edge(s, t)
        #
        #     print G_weight.number_of_edges()
        #
        #     for j in xrange(3, 16):
        #
        #         c = list(nx.k_clique_communities(G_weight, j))
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
        #     max_index = module.index(max_module)+3
        #     all_module.append([max_module, max_index])
        #
        #     cliques = list(nx.k_clique_communities(G_weight, max_index))
        #
        #     strong = 0.0
        #     for s, t in G_weight.edges():
        #         for c in cliques:
        #             if len({s, t} - set(c)) == 0:
        #                 strong += 1
        #                 break
        #
        #     all_strong.append(1 - strong / G_weight.number_of_edges())
        #
        # print all_module
        # print all_strong

        # l = []
        # for i, [m, k] in enumerate(all_module[:24]):
        #     G_weight = G_final.copy()
        #     for s, t, d in G_final.edges(data=True):
        #         if d['ks'] < i:
        #             G_weight.remove_edge(s, t)
        #
        #     c = list(nx.k_clique_communities(G_weight, k))
        #
        #     # print len(c)
        #
        #     comm_links = 0.0
        #     for m in xrange(len(c)):
        #         for n in xrange(m+1, len(c)):
        #             for a in c[m]:
        #                 for b in c[n]:
        #                     if G_weight.has_edge(a, b):
        #                         comm_links += 1
        #
        #     al = comm_links / len(c) / (len(c) - 1) * 2
        #     l.append(al)
        #     print al
        # print l

        #############################################################################
        # not recovered

        # print 'covered ratio'
        # print 1 - G_not_recovered.number_of_edges() / float(G_standard.number_of_edges())
        # print 1 - G_not_recovered_double.number_of_edges()/ float(G_double_confirmed.number_of_edges())

        # print self.distribution(G_not_recovered)

        # final_embed = sum([self.embeddedness(G_all_confirmed, s, t) for s, t in G_all_confirmed.edges()]) / float(G_all_confirmed.number_of_edges())
        # standard_embed = sum([self.embeddedness(G_standard, s, t) for s, t in G_standard.edges()]) / float(G_standard.number_of_edges())
        # recovered_embed = sum([self.embeddedness(G_all_confirmed, s, t) for s, t in G_recovered.edges()]) / float(G_recovered.number_of_edges())
        # not_recovered_embed = sum([self.embeddedness(G_all_confirmed, s, t) for s, t in G_not_recovered.edges()]) / float(G_not_recovered.number_of_edges())
        #
        # print final_embed, standard_embed, recovered_embed, not_recovered_embed
        #
        # cnt = Counter()
        # for s, t, d in G_not_recovered.edges(data=True):
        #     # if d['ks'] != 0:
        #     print s, t, d['ks'], d['weight'], self.embeddedness(G_standard, s, t)
        #
        #     cnt[d['weight'] - d['ks']] += 1
        #
        # print cnt


        # ks = []
        # for s, t in G_recovered.edges():
        #
        #     print s, t
        #
        #     nsr, ntr = 0.0, 0.0
        #     for s1, t1 in G_all_confirmed.subgraph(G_all_confirmed.neighbors(s)).edges():
        #         nsr += G_all_confirmed[s1][t1]['ks']
        #
        #     for s1, t1 in G_all_confirmed.subgraph(G_all_confirmed.neighbors(t)).edges():
        #         ntr += G_all_confirmed[s1][t1]['ks']
        #
        #     if nsr == 0 or ntr == 0:
        #         ksr = 0
        #     else:
        #         ksr = nsr / ntr if nsr < ntr else ntr / nsr
        #     # print ksr
        #     ks.append(ksr)
        #
        # print '===', sum(ks) / len(ks)
        #
        # ks = []
        # for s, t in G_not_recovered.edges():
        #
        #     nsr, ntr = 0.0, 0.0
        #     for s1, t1 in G_all_confirmed.subgraph(G_all_confirmed.neighbors(s)).edges():
        #         nsr += G_all_confirmed[s1][t1]['ks']
        #
        #     for s1, t1 in G_all_confirmed.subgraph(G_all_confirmed.neighbors(t)).edges():
        #         ntr += G_all_confirmed[s1][t1]['ks']
        #
        #     if nsr == 0 or ntr == 0:
        #         ksr = 0
        #     else:
        #         ksr = nsr / ntr if nsr < ntr else ntr / nsr
        #     # print ksr
        #     ks.append(ksr)
        # print '===', sum(ks) / len(ks)
        #
        # ks = []
        # for s, t in G_wrong.edges():
        #
        #     nsr, ntr = 0.0, 0.0
        #     for s1, t1 in G_all_confirmed.subgraph(G_all_confirmed.neighbors(s)).edges():
        #         nsr += G_all_confirmed[s1][t1]['ks']
        #
        #     for s1, t1 in G_all_confirmed.subgraph(G_all_confirmed.neighbors(t)).edges():
        #         ntr += G_all_confirmed[s1][t1]['ks']
        #
        #     if nsr == 0 or ntr == 0:
        #         ksr = 0
        #     else:
        #         ksr = nsr / ntr if nsr < ntr else ntr / nsr
        #     # print ksr
        #     ks.append(ksr)
        # print '===', sum(ks) / len(ks)


        #############################################################################
        # wrong

        # wrong_embed = sum([self.embeddedness(G_standard, s, t) for s, t in G_wrong.edges()]) / float(G_wrong.number_of_edges())
        # print wrong_embed
        # print self.variance([self.embeddedness(G_standard, s, t) for s, t in G_not_recovered.edges()])
        # print self.variance([self.embeddedness(G_standard, s, t) for s, t in G_wrong.edges()])
        #
        # # max_weight = max([d['ks'] for s, t, d in G_wrong.edges(data=True)])
        #
        # a, b, c = 0, 0, 0
        # print G_wrong.number_of_edges(), G_standard.number_of_edges(), G_all_confirmed.number_of_edges()
        # for s, t in G_wrong.edges():
        #     if not G_all_confirmed.has_edge(s, t):
        #         a += 1
        #     else:
        #         print s, t, d['ks'], d['weight'], self.embeddedness(G_standard, s, t)
        #         b += 1
        #         if G_standard.has_edge(s, t):
        #             c += 1
        # print a, b, c
        #
        # cnt = Counter()
        # for s, t, d in G_wrong.edges(data=True):
        #     if d['ks'] > 8:
        #         print s, t, d['ks'], d['weight'], self.embeddedness(G_standard, s, t)
        #     cnt[d['ks']] += 1
        # print cnt

        #############################################################################
        # weak strong tie with not recovered and wrong links

        # G_comm = G_all_confirmed.copy()
        # for s, t, d in G_comm.edges(data=True):
        #     if d['ks'] < 6:
        #         G_comm.remove_edge(s, t)
        # #
        # deleted = []
        # for n in G_comm.nodes():
        #     if G_comm.degree(n) == 0:
        #         deleted.append(n)
        #         G_comm.remove_node(n)
        #
        # comms = list(nx.k_clique_communities(G_comm, 7))
        # comms_d = list(nx.k_clique_communities(G_all_confirmed.subgraph(deleted), 4))
        # # comms.append(deleted)
        #
        # comms = comms + comms_d
        #
        # print G_comm.number_of_nodes()
        # print len({m for c in comms for m in c})
        #
        # print len(comms), self.modularity(G_all_confirmed, comms)
        # print len(comms_d)
        #
        # strong_tie = 0
        # weak_tie = 0
        # for s, t in G_not_recovered.edges():
        #     for comm in comms:
        #         if len({s, t} - set(comm)) == 0:
        #             strong_tie += 1
        #             break

        #
        # print G_recovered.number_of_edges(), strong_tie
        #
        # strong_tie = 0
        # weak_tie = 0
        # for s in G_standard.nodes():
        #     for t in G_standard.nodes():
        #         for comm in comms:
        #             if len({s, t} - set(comm)) == 0:
        #                 strong_tie += 1
        #                 break
        #             if not G_standard.has_edge(s, t):
        #                 cs = nx.cliques_containing_node(G_standard, s)
        #                 for c in cs:
        #                     tc = c[:]
        #                     sub = G_standard.subgraph(tc.append(t))
        #                     if not nx.is_connected(sub):
        #                         print s, t


        # print G_not_recovered.number_of_edges(), strong_tie
        #
        # strong_tie = 0
        # strong_tied = 0
        # for s, t in G_wrong.edges():
        #     for comm in comms:
        #         if len({s, t} - set(comm)) == 0:
        #             strong_tie += 1
        #             if G_all_confirmed.has_edge(s, t):
        #                 strong_tied += 1
        #             break
        #
        # print G_wrong.number_of_edges(), strong_tie, strong_tied

        #############################################################################
        # link prediction

        # ce, pe = [], []
        # for th in xrange(100):
        #     th /= 100.0
        #     G_predict = nx.Graph()
        #     for node in G_standard.nodes():
        #         print '==='
        #         print node
        #         G_ego = nx.ego_graph(G_standard, node, radius=2)
        #         print G_ego.number_of_edges()
        #
        #         neighbors = G_ego.neighbors(node)
        #         for s, t, d in G_ego.edges(data=True):
        #             if s not in neighbors and t not in neighbors:
        #                 G_ego.remove_edge(s, t)
        #         print G_ego.number_of_edges()
        #
        #         r = nx.resource_allocation_index(G_ego)
        #         for s, t, p in r:
        #             if p > th:
        #                 G_predict.add_edge(s, t)
        #
        #     print G_predict.number_of_edges(), G_predict.number_of_nodes()
        #
        #     cover = sum([1.0 for s, t in G_predict.edges() if G_standard.has_edge(s, t)]) / G_standard.number_of_edges()
        #     precision = sum([1.0 for s, t in G_predict.edges() if G_standard.has_edge(s, t)]) / G_predict.number_of_edges()
        #     print cover, precision
        #     ce.append(cover)
        #     pe.append(precision)
        #
        # print ce
        # print pe

        #############################################################################
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
        # # #
        # d_l, b_l, d_lg, b_lg = [], [], [], []
        # betweenness = nx.betweenness_centrality(G_standard)
        # for k, v in self.groups.items():
        #     # print [links.filter(creator=m.user).count() for m in v]
        #     d, b, lc = 0.0, 0.0, 0.0
        #     for m in v:
        #         d += G_standard.degree(m.id)
        #         b += betweenness[m.id]
        #         lc += links_new.filter(creator=m.user).count()
        #         d_l.append([G_standard.degree(m.id), links_new.filter(creator=m.user).count()])
        #         b_l.append([betweenness[m.id], links_new.filter(creator=m.user).count()])
        #
        #     d_lg.append([d/len(v), lc])
        #     b_lg.append([b/len(v), lc])
        #
        # print d_l
        # print b_l
        # print d_lg
        # print b_lg


        #############################################################################
        # crowdsourcing
        # end = 58
        # end = 12

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
        #     # count = sum([links.filter(creator=m.user).count() for m in v])
        #     group_links = links.filter(creator__in=[m.user for m in v])
        #     G_group = self.build_graph_id(group_links)
        #     group_link_count[k] = G_group.number_of_edges()
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
            if not su or not tu:
                continue
            if link.creator_id == su.id or link.creator_id == tu.id:
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

                if i % (end - 1) == 0 and i != 0:
                    f.write(str(c) + ',\n')
                    f.write(str(p) + ',\n')

                    c, p = [], []
                c.append(n[0])
                p.append(n[1])
            f.write(str(c) + ',\n')
            f.write(str(p) + ',\n')
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

    def distribution(self, G):
        return {k: v / float(G.number_of_nodes()) for k, v in dict(Counter(G.degree().values())).items()}

    def ks_distribution(self, G):
        cnt = Counter()
        for s, t, d in G.edges(data=True):
            weight = d['ks']
            if weight >=0:
                cnt[weight] += 1
        return [[k, v / float(G.number_of_edges())] for k, v in cnt.items()]

    def variance(self, seq):
        average = sum(seq) / float(len(seq))
        var = sum([abs(average - s) ** 2 for s in seq]) / float(len(seq))
        return var
