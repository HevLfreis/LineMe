#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/8/10
# Time: 15:39
from django.utils import timezone

from friendnet.methods.checking import check_credits
from friendnet.models import Credit
from LineMe.constants import LINK_BONUS


# Todo: when the link is deleted
def credit_processor(link, old_status):
    if link.status == 3 and old_status != 3:
        creator_bonus(link)

    elif old_status == 3 and link.status != 3:
        creator_punish(link)

    elif link.status == -3 and old_status != -3:
        creator_punish(link)

    elif old_status == -3 and link.status != -3:
        creator_bonus(link)

    else:
        return -1

    return 0


def creator_bonus(link):

    check_credits(link.creator, 'bonus')

    now = timezone.now()
    link.creator.extra.credits += LINK_BONUS
    link.creator.extra.save()

    c = Credit(user=link.creator,
               link=link,
               action=LINK_BONUS,
               timestamp=now)
    c.save()


def creator_punish(link):

    check_credits(link.creator, 'punish')

    now = timezone.now()
    link.creator.extra.credits -= LINK_BONUS
    link.creator.extra.save()

    c = Credit(user=link.creator,
               link=link,
               action=-LINK_BONUS,
               timestamp=now)
    c.save()


# def all_happy(link):
#     link.creator.extra.credits += LINK_BONUS
#     link.creator.extra.save()
#
#
# def peers_happy(link):
#     link.creator.extra.credits += LINK_BONUS
#     link.creator.extra.save()



# class LinkCreditManager:
#     def __init__(self, link, strategy):
#         self.link = link
#         self.strategy = strategy
#
#     def link_updated(self):
#         return
#
#     def check_credits(self, user, bonus=''):
#         if bonus == 'add':
#             if user.extra.credits > 9999:
#                 return
#         elif bonus == 'minus':
#             if user.extra.credits < LINK_BONUS:
#                 return
#         else:
#             return

