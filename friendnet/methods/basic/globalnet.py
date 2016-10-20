#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/9
# Time: 13:52
import json

from friendnet.methods.algorithm.graph import Graph, GraphAnalyzer
from friendnet.methods.basic import cache
import friendnet.methods.basic.exp as exp
from friendnet.models import Group


@cache.get_or_set('globalcore')
def get_user_global_core(groupid):
    return Graph(Group.objects.get(id=groupid)).core_builder()


@cache.get_or_set('global')
def get_user_global_basic(user, groupid):
    # return Graph(Group.objects.get(id=groupid)).global_builder(user)
    return get_user_global_core(groupid).core(user)


# def get_user_global_graph(user, groupid):
#     return Graph(user, Group.objects.get(id=groupid)).global_builder().color().dictify()
#
#
# def get_user_global_map(user, groupid):
#     return Graph(user, Group.objects.get(id=groupid)).global_builder().map_dictify()
#
#
# def get_user_global_info(user, groupid):
#     return graph_analyzer(user, groupid)


@cache.get_or_set('globalnet')
def get_user_global_graph(user, groupid):
    # without color, save 70% time
    return get_user_global_basic(user, groupid).dictify()


@cache.get_or_set('globalmap')
def get_user_global_map(user, groupid):
    return get_user_global_basic(user, groupid).map_dictify()


@cache.get_or_set('globalthree')
def get_user_global_three(groupid):
    return get_user_global_core(groupid).three_dictify()


@cache.get_or_set('globalinfo')
def get_user_global_info(user, groupid):
    return graph_analyzer(user, groupid)


def get_user_global_exp(user, groupid):
    func = exp.global_core
    G = Graph(Group.objects.get(id=groupid)).global_builder(user).color()
    return G.dictify()


# Todo: link status should be 3
# Todo: most contributor ? get most credits
def graph_analyzer(user, groupid):
    # Global = Graph(user, Group.objects.get(id=groupid)).global_builder()
    Global = get_user_global_basic(user, groupid)
    G = Global.bingo()
    my_member = Global.myself()

    # Todo: exception
    if my_member is None:
        raise Exception('Member is None')

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
    average_distance = analyzer.average_shortest_path_length()

    best_friend, bf_ratio = analyzer.best_friend()

    # Todo: ratio not correct fixed...
    heart = Global.heart()

    return {'distribution': json.dumps(distribution),
            'top3': top3,
            'my_rank': rank,
            'average_degree': average_degree,
            'average_distance': average_distance,
            'cover': round(cover * 100, 2),
            'bestfriend': best_friend,
            'bf_ratio': round(bf_ratio * 100, 2),
            'heart': heart}
