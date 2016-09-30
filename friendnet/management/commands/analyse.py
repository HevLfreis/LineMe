import networkx as nx

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

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
        # for user in options['user']:
        #     for group in options['group']:
        #
        #         try:
        #             user = User.objects.get(username=user.lower())
        #             group = Group.objects.get(group_name=group.upper())
        #         except Link.DoesNotExist:
        #             raise CommandError('Group "%s" does not exist' % group)
        self.analyzer()

        return

    def analyzer(self):
        G = nx.Graph()

        members = GroupMember.objects.filter(group_id=10001)
        mycount, othercount = {}, {}
        for member in members:
            if member.user:
                links = Link.objects.filter(
                    group__id=10001,
                    creator=member.user
                )

                mylinks = links.filter((Q(source_member=member) | Q(target_member=member)))
                otherlinks = links.exclude((Q(source_member=member) | Q(target_member=member)))

                mycount[member] = mylinks.count()
                othercount[member] = otherlinks.count()

        s = 0
        zero = 0
        for k, v in mycount.items():
            s += v
            if v == 0:
                zero += 1

        print 'my sum: ', s, zero

        s = 0
        zero = 0
        for k, v in othercount.items():
            s += v
            if v == 0:
                zero += 1

        print 'other sum: ', s, zero

        maxfriend = max(mycount, key=mycount.get)
        minfriend = min(mycount, key=mycount.get)

        print maxfriend.member_name, mycount[maxfriend]
        print minfriend.member_name, mycount[minfriend]

        maxfriend = max(othercount, key=othercount.get)
        minfriend = min(othercount, key=othercount.get)

        print maxfriend.member_name, mycount[maxfriend]
        print minfriend.member_name, mycount[minfriend]


        # mycountsort = sorted(mycount.items(), key=lambda x:x[1], reverse=True)
        # othercountsort = sorted(othercount.items(), key=lambda x:x[1], reverse=True)
        # print mycountsort, othercountsort

        # links1 = links1 = Link.objects.filter(
        #     group__id=10001,
        #     status=3
        # )
        # links2 = Link.objects.filter(
        #     group__id=10001,
        #     status__gt=0
        # ).exclude(status=3)
        # links3 = Link.objects.filter(
        #     group__id=10001,
        #     status=0
        # )
        #
        # for link in links1:
        #     G.add_edge(link.source_member.id, link.target_member.id, status=3)
        #
        # for link in links2:
        #     G.add_edge(link.source_member.id, link.target_member.id, status=2)
        #
        # for link in links3:
        #     G.add_edge(link.source_member.id, link.target_member.id, status=1)
        #
        # c1, c2, c3 = 0, 0, 0
        # for s, t, d in G.edges(data=True):
        #     if d['status'] == 3:
        #         c1 += 1
        #     elif d['status'] == 2:
        #         c2 += 1
        #     elif d['status'] == 1:
        #         c3 += 1
        #
        # print c1, c2, c3
        #
        #
        # #
        # # for link in links:
        # #     G.add_edge(link.source_member.id, link.target_member.id)
        # #
        # # average_degree = 2.0 * G.number_of_edges() / G.number_of_nodes()
        # #
        # # print group, average_degree
        # # G = Graph(user, group).global_builder(color=True).bingo()
        #
        # print G.number_of_nodes(), G.number_of_edges()





