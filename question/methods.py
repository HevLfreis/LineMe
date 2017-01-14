#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/12/10
# Time: 11:06

"""
Question type:
Normal: n
Single selection: s
Multiple selection: m
Single member selection: sm
Multiple member selection: mm
"""
import json

from LineMe.constants import QUESTION_TEMPLATE_KEYS
from LineMe.utils import md5, input_filter
from question.models import QuestionTemplate


class Questionnaire:
    def __init__(self, groupid):
        self.groupid = groupid
        self.questions = None
        self.qt = QuestionTemplate.objects.get(group__id=self.groupid)
        self.question_keys = QUESTION_TEMPLATE_KEYS
        self.CHOICES_LIMIT = 20

    def proceeding(self, request):
        if not self.qt.authenticated:
            return

        self.questions = json.loads(request.POST.get('questions'))

    def save(self):
        if not self.questions:
            return

        for question in self.questions:
            if self.__check_and_filter(question):
                question['id'] = md5(question['title'])
            else:
                pass

        self.qt.template = self.questions
        self.qt.save()

    def __check_and_filter(self, question):
        if 'type' not in question or 'title' not in question:
            return False

        keys = set(question.keys()) - {'type'}
        question['title'] = input_filter(question['title'])

        if self.question_keys['normal'] == keys:
            question['placeholder'] = input_filter(question['placeholder'])

        elif self.question_keys['single'] == keys:
            if not self.__choices_check_and_filter(question):
                return False

        elif self.question_keys['multiple'] == keys:
            if not self.__choices_check_and_filter(question):
                return False

            if type(question['limit']) is not int:
                return False

            if question['limit'] > len(question['choices']):
                question['limit'] = len(question['choices'])

        elif self.question_keys['single_member'] == keys:
            pass

        elif self.question_keys['multiple_member'] == keys:
            pass

        else:
            return False

        return True

    @staticmethod
    def __choices_check_and_filter(question):
        choices = question['choices']
        if type(choices) is not list or len(choices) == 0:
            return False
        question['choices'] = map(input_filter, choices[:20])

        print question['choices']

        return True



