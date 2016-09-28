import networkx as nx

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from LineMe.constants import PROJECT_NAME
from friendnet.methods.algorithm.graph import Graph
from friendnet.models import Link, Group


class Command(BaseCommand):
    help = 'Analysis Links of ' + PROJECT_NAME

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--user', action='append')
        parser.add_argument('--group', action='append')

    def handle(self, *args, **options):
        for user in options['user']:
            for group in options['group']:

                try:
                    user = User.objects.get(username=user.lower())
                    group = Group.objects.get(group_name=group.upper())
                except Link.DoesNotExist:
                    raise CommandError('Group "%s" does not exist' % group)
                self.analyzer(user, group)

        return

    def analyzer(self, user, group):
        # G = nx.Graph()
        #
        # for link in links:
        #     G.add_edge(link.source_member.id, link.target_member.id)
        #
        # average_degree = 2.0 * G.number_of_edges() / G.number_of_nodes()
        #
        # print group, average_degree
        G = Graph(user, group).global_builder(color=True).bingo()

        print G.number_of_nodes(), G.number_of_edges()





