#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/9
# Time: 13:52
import random

from friendnet.methods.algorithm.graph import Graph
from friendnet.models import GroupMember, Group
from friendnet.models import Link


def get_user_ego_graph(user, groupid):
    # ls = Link.objects.filter(
    #     group__id=groupid,
    #     creator=user
    # )
    #
    # gms, nodes, links = [], [], []
    #
    # self = GroupMember.objects.get(
    #     group__id=groupid,
    #     user=user,
    #     is_joined=True
    # )
    #
    # nodes.append({'id': self.id,
    #               'userid': self.user.id,
    #               'name': self.member_name,
    #               'self': True,
    #               'group': 0})
    #
    # if ls.count() != 0:
    #
    #     for link in ls:
    #
    #         if link.source_member not in gms and link.source_member != self:
    #             gms.append(link.source_member)
    #         if link.target_member not in gms and link.target_member != self:
    #             gms.append(link.target_member)
    #
    #     # Todo: implement group color
    #     for gm in gms:
    #         nodes.append({'id': gm.id,
    #                       'userid': (-1 if gm.user is None else gm.user.id),
    #                       'name': gm.member_name,
    #                       'self': False,
    #                       'group': random.randint(1, 4)})
    #
    #     for link in ls:
    #         links.append({'id': link.id,
    #                       'source': link.source_member.id,
    #                       'target': link.target_member.id,
    #                       'status': link.status,
    #                       'value': 1,
    #                       'group': link.group.id})

    G = Graph(user, Group.objects.get(id=groupid)).ego_builder().jsonify()

    return G
