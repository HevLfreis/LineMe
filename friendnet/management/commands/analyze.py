#!/usr/bin/env python
# coding: utf-8
import copy
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
from friendnet.methods.basic.user import get_user_name
from friendnet.models import Link, Group, GroupMember
# import matplotlib.pyplot as plt


class Command(BaseCommand):
    help = 'Analysis Links of ' + PROJECT_NAME
    members = None

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('-g', '--group', type=int)

    def handle(self, *args, **options):
        self.analyzer(options['group'])

        return

    def analyzer(self, groupid):
        self.members = GroupMember.objects.filter(group__id=groupid, is_joined=True)

        for m in GroupMember.objects.filter(group__id=groupid, is_joined=False):
            print m.member_name

        male_count = self.members.filter(user__extra__gender=False).count()
        female_count = self.members.filter(user__extra__gender=True).count()

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
        print 'average added friends fenmale: ', links_female.count() / float(female_count)
        print 'average added friends: ', friend_links.count() / float(self.members.count()), '\n'

        # G_all = self.build_graph(links)
        # G_friend = self.build_graph(friend_links)
        # G_other = self.build_graph(other_links)
        #
        G_all_confirmed = self.build_graph(links_confirmed)
        # G_friend_confirmed = self.build_graph(friend_links_confirmed)
        # G_other_confirmed = self.build_graph(other_links_confirmed)

        # G_all_unconfirmed = self.build_graph(links_unconfirmed)
        # G_friend_unconfirmed = self.build_graph(friend_links_unconfirmed)
        # G_other_unconfirmed = self.build_graph(other_links_unconfirmed)

        self.print_info(G_all_confirmed, 'u')

        # single node
        # s, n, u, z, o = 0, 0, 0, 0, 0
        # for m in G_all_confirmed.nodes():
        #     if G_all_confirmed.degree(m) == 0:
        #         s += 1
        #         if m.user is None:
        #             n += 1
        #             print get_user_name(m.user), 'not in'
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
        # print s, n, u, z, o


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
        # wc = {}
        # bi, nb = 0.0, 0.0
        # for (s, t, d) in G_all_confirmed.edges(data=True):
        #     w = d['weight']
        #     if w in wc:
        #         wc[w] += 1
        #     else:
        #         wc[w] = 1
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
            if not G.has_edge(link.source_member, link.target_member):
                G.add_edge(link.source_member, link.target_member, link=[link], weight=1)
            else:
                G[link.source_member][link.target_member]['weight'] += 1
                G[link.source_member][link.target_member]['link'].append(link)
        return G

    def confirmed(self, links):
        return links.filter(status=3)

    def unconfirmed(self, links):
        return links.exclude(status=3)

    def single_rejected(self, links):
        return links.filter(status__lt=0).exclude(status=-3)

    def both_rejected(self, links):
        return links.filter(status=-3)

    def print_info(self, G, name):
        print name
        print 'nodes: ', G.number_of_nodes(), ' links: ', G.number_of_edges()
        print 'average degree: ', self.average_degree(G), 'average_shortest_path: ', self.average_shortest_path_length(G)

    def average_degree(self, G):
        return 2.0 * G.number_of_edges() / G.number_of_nodes()

    def average_shortest_path_length(self, G):
        d = [nx.average_shortest_path_length(g) for g in nx.connected_component_subgraphs(G) if g.number_of_nodes() > 1]
        print '(', len(d), 'component)',
        return sum(d) / len(d)

    def connected_component(self, G):
        for g in nx.connected_component_subgraphs(G):
            if g.number_of_nodes() != 1:
                print g.number_of_nodes(), g.number_of_edges()

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










