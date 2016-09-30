import networkx as nx

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q, F

from LineMe.constants import PROJECT_NAME
# from friendnet.methods.algorithm.graph import Graph
from friendnet.models import Link, Group, GroupMember


class Command(BaseCommand):
    help = 'Analysis Links of ' + PROJECT_NAME

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--user', action='append')
        parser.add_argument('--group', action='append')

    def handle(self, *args, **options):
        self.analyzer()

        return

    def analyzer(self):

        members = GroupMember.objects.filter(group__id=10001, is_joined=True)

        links = Link.objects.filter(group__id=10001)
        friend_links = links.filter(Q(source_member__user=F('creator')) | Q(target_member__user=F('creator')))
        other_links = links.exclude(Q(source_member__user=F('creator')) | Q(target_member__user=F('creator')))

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

        print 'average added friends: ', friend_links.count() / float(members.count()), '\n'

        G_all = self.build_graph(links)
        G_friend = self.build_graph(friend_links)
        G_other = self.build_graph(other_links)

        G_all_confirmed = self.build_graph(links_confirmed)
        G_friend_confirmed = self.build_graph(friend_links_confirmed)
        G_other_confirmed = self.build_graph(other_links_confirmed)

        G_all_unconfirmed = self.build_graph(links_unconfirmed)
        G_friend_unconfirmed = self.build_graph(friend_links_unconfirmed)
        G_other_unconfirmed = self.build_graph(other_links_unconfirmed)

        c = 0.0
        for (s, t) in G_all_unconfirmed.edges():
            if G_all_confirmed.has_edge(s, t):
                c += 1
                print s.member_name, t.member_name

        print 'ratio: ', c / G_all_unconfirmed.number_of_nodes()

        print 'all'
        self.print_info(G_all)
        print 'average degree: ', self.average_degree(G_all)
        print 'average distance: ', self.average_shortest_path_length(G_all), '\n'

        print 'friend'
        self.print_info(G_friend)
        print 'average degree: ', self.average_degree(G_friend)
        print 'average distance: ', self.average_shortest_path_length(G_friend), '\n'

        print 'other'
        self.print_info(G_other)
        print 'average degree: ', self.average_degree(G_other)
        print 'average distance: ', self.average_shortest_path_length(G_other), '\n'

        print 'all confirmed'
        self.print_info(G_all_confirmed)
        print 'average degree: ', self.average_degree(G_all_confirmed)
        print 'average distance: ', self.average_shortest_path_length(G_all_confirmed), '\n'

        print 'friend confirmed'
        self.print_info(G_friend_confirmed)
        print 'average degree: ', self.average_degree(G_friend_confirmed)
        print 'average distance: ', self.average_shortest_path_length(G_friend_confirmed), '\n'

        print 'other confirmed'
        self.print_info(G_other_confirmed)
        print 'average degree: ', self.average_degree(G_other_confirmed)
        print 'average distance: ', self.average_shortest_path_length(G_other_confirmed), '\n'

        print 'all unconfirmed'
        self.print_info(G_all_unconfirmed)
        print 'average degree: ', self.average_degree(G_all_unconfirmed)
        print 'average distance: ', self.average_shortest_path_length(G_all_unconfirmed), '\n'

        print 'friend unconfirmed'
        self.print_info(G_friend_unconfirmed)
        print 'average degree: ', self.average_degree(G_friend_unconfirmed)
        print 'average distance: ', self.average_shortest_path_length(G_friend_unconfirmed), '\n'

        print 'other unconfirmed'
        self.print_info(G_other_unconfirmed)
        print 'average degree: ', self.average_degree(G_other_unconfirmed)
        print 'average distance: ', self.average_shortest_path_length(G_other_unconfirmed), '\n'



    def build_graph(self, links):
        G = nx.Graph()
        for link in links:
            if not G.has_edge(link.source_member, link.target_member):
                G.add_edge(link.source_member, link.target_member, id=link.id, weight=1)
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

        d = [nx.average_shortest_path_length(g) for g in nx.connected_component_subgraphs(G)]

        return sum(d) / len(d)








