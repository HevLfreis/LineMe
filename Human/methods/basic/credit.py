#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/8/10
# Time: 15:39
from django.utils import timezone

from Human.methods.validation import check_credits
from Human.models import Credit
from LineMe.constants import LINK_BONUS


def credit_processor(link, old_status):
    if link.status == 3 and old_status != 3:
        bonus_link(link, 'creator')

    elif old_status == 3 and link.status != 3:
        bonus_link(link, 'reverse')

    return 0


def bonus_link(link, bonus=''):
    if bonus == 'creator':
        check_credits(link.creator, 'add')
        creator_happy(link)

    elif bonus == 'reverse':
        check_credits(link.creator, 'minus')
        creator_punish(link)

    elif bonus == 'all':
        check_credits(link.creator, 'add')
        all_happy(link)

    else:
        creator_happy(link)


def bonus_reverse(link):

    now = timezone.now()
    link.creator.extra.credits -= LINK_BONUS
    link.creator.extra.save()

    c = Credit(user=link.creator,
               link=link,
               action=-LINK_BONUS,
               timestamp=now)
    c.save()


def creator_happy(link):

    now = timezone.now()
    link.creator.extra.credits += LINK_BONUS
    link.creator.extra.save()

    c = Credit(user=link.creator,
               link=link,
               action=LINK_BONUS,
               timestamp=now)
    c.save()


def creator_punish(link):

    now = timezone.now()
    link.creator.extra.credits -= LINK_BONUS
    link.creator.extra.save()

    c = Credit(user=link.creator,
               link=link,
               action=-LINK_BONUS,
               timestamp=now)
    c.save()


def all_happy(link):
    link.creator.extra.credits += LINK_BONUS
    link.creator.extra.save()


def others_happy(link):
    link.creator.extra.credits += LINK_BONUS
    link.creator.extra.save()
