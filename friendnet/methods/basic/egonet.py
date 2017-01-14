#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/9
# Time: 13:52

from friendnet.methods.algorithm.graph import LGraph
from friendnet.models import Group


def get_user_ego_graph(user, groupid):
    return LGraph(Group.objects.get(id=groupid)).ego_builder(user).jsonify()
