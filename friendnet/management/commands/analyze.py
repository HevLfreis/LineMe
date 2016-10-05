#!/usr/bin/env python
# coding: utf-8
import datetime
import json

import networkx as nx
import operator

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q, F

from LineMe.constants import PROJECT_NAME
# from friendnet.methods.algorithm.graph import Graph
from friendnet.methods.algorithm.graph import Graph
from friendnet.models import Link, Group, GroupMember
# import matplotlib.pyplot as plt


class Command(BaseCommand):
    help = 'Analysis Links of ' + PROJECT_NAME
    members = None

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--user', action='append')
        parser.add_argument('--group', action='append')

    def handle(self, *args, **options):
        self.analyzer()

        return

    def analyzer(self):

        self.members = GroupMember.objects.filter(group__id=10001, is_joined=True)


        male_count = self.members.filter(user__extra__gender=False).count()
        female_count = self.members.filter(user__extra__gender=True).count()

        links = Link.objects.filter(group__id=10001)
        friend_links = links.filter(Q(source_member__user=F('creator')) | Q(target_member__user=F('creator')))
        other_links = links.exclude(Q(source_member__user=F('creator')) | Q(target_member__user=F('creator')))

        for m in self.members:
            if m is not None:
                G = Graph(m.user, Group.objects.get(id=10001)).ego_builder().bingo()
                es = links.filter(creator=m.user)

                for e in es:
                    if not G.has_edge(e.source_member, e.target_member):
                        print m.user, es.count(), G.number_of_edges()
                        break

                if es.count() != G.number_of_edges():
                    print m.user, es.count(), G.number_of_edges()
        # link = links.get(status=-3)
        # print male_count, female_count

        print 'total links: ', links.count()
        # links_male = friend_links.filter(creator__extra__gender=False)
        # links_female = friend_links.filter(creator__extra__gender=True)
        # print 'total links male: ', links_male.count()
        # print 'total links female: ', links_female.count()
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

        # print 'average added friends male: ', links_male.count() / float(male_count)
        # print 'average added friends fenmale: ', links_female.count() / float(female_count)
        print 'average added friends: ', friend_links.count() / float(self.members.count()), '\n'

        # for link in links:
        #     simi = links.filter((Q(source_member=link.source_member, target_member=link.target_member) |
        #                         Q(source_member=link.target_member, target_member=link.source_member)),
        #                         creator=link.creator).exclude(id=link.id)
        #     if simi.exists():
        #
        #         print link.creator
                #
                # for l in simi:
                #     print l.id
                #
                # print ''
        # G_all = self.build_graph(links)
        # G_friend = self.build_graph(friend_links)
        # G_other = self.build_graph(other_links)

        # G_all_confirmed = self.build_graph(links_confirmed)
        # G_friend_confirmed = self.build_graph(friend_links_confirmed)
        # G_other_confirmed = self.build_graph(other_links_confirmed)

        # G_all_unconfirmed = self.build_graph(links_unconfirmed)
        # G_friend_unconfirmed = self.build_graph(friend_links_unconfirmed)
        # G_other_unconfirmed = self.build_graph(other_links_unconfirmed)

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


        # d = {i * 10: 0 for i in xrange(11)}
        # for m in self.members:
        #
        #     m_links = links.filter(Q(source_member=m) | Q(target_member=m)).exclude(creator=m.user)
        #     if m_links.count() == 0:
        #         r = 0
        #     else:
        #
        #         r = m_links.filter(status=3).count() / float(m_links.count())
        #     # print r, int(r*100)/10*10
        #     if r < 0.4:
        #         print m.member_name, r, m_links.count(), G_all_confirmed.degree(m)
        #     d[int(r*100)/10*10] += 1
        #     # a = raw_input()
        #
        # print d

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



    def build_graph(self, links):
        G = nx.Graph()
        # for m in self.members:
        #     G.add_node(m)

        for link in links:
            if not G.has_edge(link.source_member, link.target_member):
                G.add_edge(link.source_member, link.target_member, link=link, weight=1)
            else:
                G[link.source_member][link.target_member]['weight'] += 1
        return G

    def confirmed(self, links):
        return links.filter(status=3)

    def unconfirmed(self, links):
        return links.exclude(status=3)


    def print_info(self, G):
        print 'nodes: ', G.number_of_nodes(), ' links: ', G.number_of_edges()

    def average_degree(self, G):
        return 2.0 * G.number_of_edges() / G.number_of_nodes()

    def average_shortest_path_length(self, G):

        d = [nx.average_shortest_path_length(g) for g in nx.connected_component_subgraphs(G) if g.number_of_nodes() > 1]
        print len(d),
        return sum(d) / len(d)








