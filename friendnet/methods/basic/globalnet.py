#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/9
# Time: 13:52

from friendnet.methods.algorithm.graph import graph_analyzer, Graph
from friendnet.models import Group


def get_user_global_graph(user, groupid):
    return Graph(user, Group.objects.get(id=groupid)).global_builder(color=True).dictify()


def get_user_global_map(user, groupid):
    return Graph(user, Group.objects.get(id=groupid)).global_builder().map_dictify()


def get_user_global_info(user, groupid):
    return graph_analyzer(user, groupid)
