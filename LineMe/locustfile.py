#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/9/13
# Time: 13:30
from locust import HttpLocust, TaskSet


def login(l):
    l.client.post("/login/", {"username": "tengyansong", "password": "123456"})


def home(l):
    l.client.get("/home")


def ego(l):
    l.client.get("/ego/10001")
    l.client.get("/egraph/10001")


def glo(l):
    l.client.get("/global/10001")
    l.client.get("/ggraph/10001")
    l.client.get("/gmap/10001")
    l.client.get("/gthree/10001")


def profile(l):
    l.client.get("/profile")


def static(l):
    l.client.get("/static/plugins/jquery/jquery.min.js")
    l.client.get("/static/bootstrap/js/bootstrap.min.js")
    l.client.get("/static/dist/js/app.min.js")
    l.client.get("/static/lineme/js/rollbar.js")
    l.client.get("/static/lineme/js/autocomplete.js")
    l.client.get("/static/lineme/js/analytics.js")
    l.client.get("/static/bootstrap/css/bootstrap.min.css")
    l.client.get("/static/dist/css/AdminLTE.css")
    l.client.get("/static/dist/css/skins/skin-black.css")


def logout(l):
    l.client.get("/logout")


class UserBehavior(TaskSet):
    tasks = {home: 2, ego: 2, glo: 2, profile: 1}

    def on_start(self):
        login(self)


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
