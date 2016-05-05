import base64
import json
import logging
import random
import re
import datetime
import cStringIO
from PIL import Image
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, render_to_response
from django.template import loader, Context
from django.template import RequestContext
import time
from sympy import Li
from LineMe.settings import STATICFILES_DIRS
from Human.constants import PROJECT_NAME, GROUP_MAXSIZE, GROUP_CREATED_CREDITS_COST, PROJECT_FOLDER
from Human.forms import RegisterForm, LoginForm, GroupCreateForm, GroupMemberCreateForm, ReJoinIdentifierForm
from Human.models import Group, GroupMember, Credits, Privacy, Extra, Link
import networkx as nx


# Create your views here.


@login_required
def home(request):

    user = request.user
    groups = get_user_groups(user)
    my_groups = {}
    in_groups = {}

    for group in groups:
        if group.creator == user:
            my_groups.setdefault(group, get_group_joined_num(group))
        else:
            in_groups.setdefault(group, get_group_joined_num(group))

    context = Context({"project_name": PROJECT_NAME, "user": user, "my_groups": my_groups, "in_groups": in_groups})
    return render_to_response('Human/home.html', context)


@login_required
def ego(request):
    user = request.user
    groups = get_user_groups(user)
    sug_group = get_group_suggestions(user)


    groupid = check_groupid(request.GET.get('groupid'))

    # sug_groupmember = get_member_suggestions(user, groupid)
    # print groupid

    # for g in groups:
    #     print g.group_name
    context = Context({"project_name": PROJECT_NAME, "user": user, "groups": groups, "groupid": groupid,
                       "sug_group": sug_group, "status": 0})

    if request.method == 'POST':
        gf = GroupCreateForm(request.POST)

        if gf.is_valid():
            name = gf.cleaned_data['name']
            maxsize = gf.cleaned_data['maxsize']
            identifier = int(gf.cleaned_data['identifier'])

            # ---- type = 0
            status = create_group(request, name, maxsize, identifier, 0)
            context["status"] = status
            if status == 0:
                print 'new group created: ', name, maxsize, identifier

                groupid = Group.objects.get(group_name=name).id
                return HttpResponseRedirect('/cnc/group?groupid='+str(groupid))
            else:
                return render_to_response('Human/ego.html', context)
        else:
            context["status"] = 1
            return render_to_response('Human/ego.html', context)

    return render_to_response('Human/ego.html', context)


@login_required
def graph(request, groupid):
    user = request.user
    if groupid == '0':
        return HttpResponse(json.dumps({"nodes": None, "links": None}))
    print "graph groupid: ", groupid

    gms = []
    ls = Link.objects.filter(group__id=groupid, creator=user)

    data = {}
    nodes = []
    links = []

    self = GroupMember.objects.get(group__id=groupid, user=user)
    nodes.append({'id': self.id, 'userid': self.user.id, 'name': self.member_name,
                  'self': True, 'group': 0})

    if ls.count() != 0:

        for link in ls:

            if link.from_member not in gms and link.from_member != self:
                gms.append(link.from_member)
            if link.to_member not in gms and link.to_member != self:
                gms.append(link.to_member)

        # print gms

        try:
            for gm in gms:

                nodes.append({'id': gm.id, 'userid': (-1 if gm.user is None else gm.user.id), 'name': gm.member_name,
                              'self': False, 'group': random.randint(1, 4)})
                # nodes.append({'id': str(gm.id), 'group': random.randint(0, 3)})

            for link in ls:
                links.append({'id': link.id, 'source': link.from_member.id, 'target': link.to_member.id,
                              'status': link.status, 'value': 1, 'group': link.group.id})
                # links.append({'source': str(link.from_membe

        except Exception, e:
            print e

    data.setdefault("nodes", nodes)
    data.setdefault("links", links)

    # print data

    return HttpResponse(json.dumps(data))


@login_required
def sugmember(request, groupid, page):
    user = request.user
    if request.is_ajax():
        # groupid = check_groupid(request.GET.get('groupid'))
        if groupid == '0':
            return render(request, 'Human/ego_sub.html')

        sug_groupmember = get_member_suggestions(user, groupid)

        paginator = Paginator(sug_groupmember, 6)

        try:
            p = paginator.page(page)
        except PageNotAnInteger:
            p = paginator.page(1)
        except EmptyPage:
            p = paginator.page(paginator.num_pages)

        return render(request, 'Human/ego_sub.html', {'sug_groupmember': p})
    else:
        raise Http404


@login_required
def links(request, groupid):
    user = request.user
    if request.is_ajax():
        newLinks = request.POST.get('links')

        # print newLinks
        # print eval(newLinks)

        oldLinks = Link.objects.filter(creator=user, group__id=groupid)
        LinksDict = {}

        for link in oldLinks:
            LinksDict[str(link.from_member.id)+','+str(link.to_member.id)] = link

        for link in eval(newLinks):
            if link["source"]+','+link["target"] in LinksDict:
                LinksDict[link["source"]+','+link["target"]] = 0
            elif link["target"]+','+link["source"] in LinksDict:
                LinksDict[link["target"]+','+link["source"]] = 0
            else:
                LinksDict[link["source"]+','+link["target"]] = 1

        user_groupmember_id = GroupMember.objects.get(group__id=groupid, user=user).id

        for k, v in LinksDict.items():
            if v is 0:
                continue
            elif v is 1:
                try:
                    source = int(k.split(',')[0])
                    target = int(k.split(',')[1])
                    if source == user_groupmember_id:
                        status = 1
                    elif target == user_groupmember_id:
                        status = 2
                    else:
                        status = 0
                    now = datetime.datetime.now()

                    l = Link(creator=user,
                             from_member_id=source,
                             to_member_id=target,
                             group_id=groupid,
                             status=status,
                             created_time=now)
                    l.save()

                except Exception, e:
                    print e
            else:
                v.delete()

        return HttpResponse("Link update successfully")




@login_required
def manage_group(request):
    user = request.user
    groups = get_user_groups(user)
    sug = get_group_suggestions(user)

    # print sug
    context = Context({"project_name": PROJECT_NAME, "user": user, "groups": groups,
                       "sug": sug, "status": 0})

    groupid = request.GET.get('groupid')
    group = Group.objects.get(id=groupid)

    if groupid != check_groupid(groupid):
        raise Http404

    if request.method == 'POST':
        gf = GroupMemberCreateForm(request.POST)
        print gf.is_valid()
        if gf.is_valid():
            name = gf.cleaned_data['name']
            identifier = gf.cleaned_data['identifier']

            # dangerous
            status = create_group_member(group, name, identifier)
            if status == 0:
                print 'new group member created: ', name, identifier
            return HttpResponseRedirect('/cnc/group?groupid='+str(groupid))

    joined = request.GET.get('joined')

    if joined == '0':
        context.push(joined=0)
    elif joined == '1':
        context.push(joined=1)

    members = GroupMember.objects.filter(group=group)
    context.push(group=group, members=members)
    if user != group.creator:

        members_count = members.count()

        # -----
        if GroupMember.objects.filter(group=group, user=user, is_joined=True).exists():
            is_member = True
        else:
            is_member = False
        context.push(creator=group.creator, members_count=members_count, is_member=is_member)
        return render_to_response('Human/group2.html', context)

    else:
        members_count = GroupMember.objects.filter(group=group).count()
        context.push(creator=user,  members_count=members_count)
        return render_to_response('Human/group1.html', context)


@login_required
def join(request):

    user = request.user
    if request.is_ajax():
        groupid = int(request.POST.get('groupid'))
        identifier = request.POST.get('identifier')
        print 'join:', groupid, identifier
        group = Group.objects.get(id=groupid)
        gm = GroupMember.objects.filter(group=group, member_name=get_user_name(user))
        if not gm.exists():
            return HttpResponse(-2)

        if group.identifier == 0:

            if gm.filter(token=user.email).exists():
                member_join(user, group, user.email)
                return HttpResponse(0)
            else:
                return HttpResponse(-1)
        elif group.identifier == 1:
            if gm.filter(token=user.institution).exists():
                member_join(user, group, user.institution)
                return HttpResponse(1)
            else:
                return HttpResponse(-1)

        elif group.identifier == 2:
            if gm.filter(token=identifier).exists():
                member_join(user, group, identifier)
                return HttpResponse(2)
            else:
                return HttpResponse(-1)

        else:
            print ''
            raise Exception
    elif request.method == 'POST':
        rf = ReJoinIdentifierForm(request.POST)
        print rf.is_valid()
        if rf.is_valid():
            groupid = int(rf.cleaned_data['groupid'])
            group = Group.objects.get(id=groupid)
            identifier = rf.cleaned_data['identifier']
            print 'rejoin: ', groupid, identifier
            if identifier != '':
                if GroupMember.objects.filter(group=group, member_name=get_user_name(user), token=identifier).exists():
                    member_join(user, group, identifier)
                    return HttpResponseRedirect('/cnc/group?groupid='+str(groupid)+'&joined=0')

        # -----
        groupid = int(rf.cleaned_data['groupid'])
        return HttpResponseRedirect('/cnc/group?groupid='+str(groupid)+'&joined=1')


def my_login(request):
    context = Context({"project_name": PROJECT_NAME, "status": ''})
    if request.method == 'POST':
        lf = LoginForm(request.POST)
        print lf.is_valid()
        if lf.is_valid():
            email = lf.cleaned_data['email']
            password = lf.cleaned_data['password']
            print 'login: ', email, password
            try:
                u = User.objects.get(email=email)
            except User.DoesNotExist:
                context["status"] = 'Account does not existed'
                return render_to_response('Human/login.html', context)

            user = authenticate(username=u.username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect("/cnc/home")
                else:
                    return HttpResponseRedirect("/cnc/login")
            else:
                context["status"] = 'Wrong password !'
                return render_to_response('Human/login.html', context)

    return render_to_response('Human/login.html', context)


def my_logout(request):
    logout(request)
    context = Context({"project_name": PROJECT_NAME})
    return render_to_response('Human/login.html', context)


def my_register(request):

    # status 0 :
    # status 1 : wrong name
    # status 2 : wrong email
    # status 3 : wrong password
    context = Context({"project_name": PROJECT_NAME, "status": 0})
    if request.method == 'POST':
        rf = RegisterForm(request.POST)
        print 'Register Form valid: ', rf.is_valid()
        if rf.is_valid():
            name = rf.cleaned_data['name']
            email = rf.cleaned_data['email']
            password = rf.cleaned_data['password']
            password2 = rf.cleaned_data['password2']

            status = create_user(name, email, password, password2)
            context["status"] = status
            # print name, password, email

            if status == 0:
                print 'New user', 'created: ', name
                user = authenticate(username=name, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return HttpResponseRedirect("/cnc/demo")
                    else:
                        return HttpResponseRedirect("/cnc/login")
                else:
                    return HttpResponseRedirect("/cnc/404")

            return render_to_response('Human/register.html', context)
        else:
            return render_to_response('Human/register.html', context)

    # print context
    return render_to_response('Human/register.html', context)


@login_required()
def avatar(request):

    user = request.user

    context = Context({"project_name": PROJECT_NAME, "user": user})
    return render_to_response('Human/avatar.html', context)


@login_required
def imghandle(request):
    if request.is_ajax():
        # process the image
        # print 'avatar ajax received'
        userid = request.user.id
        try:
            # print request.POST['imgBase64']
            image_string = cStringIO.StringIO(base64.b64decode(request.POST['imgBase64'].partition('base64,')[2]))
            image = Image.open(image_string)
            # image.save(pic, )
            image.save(PROJECT_FOLDER+"/pic/avatar/"+str(userid)+".png", image.format, quality=100)
            # print image.format, image.size, image.mode
        except Exception, e:
            print e
            return HttpResponse('Upload failed')

        return HttpResponse('Upload success')


def error_404(request):
    context = Context({"project_name": PROJECT_NAME})
    return render_to_response('Human/error/404.html', context)


#####################################################################################


def get_user_name(user):
    last = user.last_name
    first = user.first_name
    if len(first) is 0 and len(last) is 0:
        return user.username
    else:
        return last+' no'+first


def get_user_groups(user):
    gms = GroupMember.objects.filter(user=user, is_joined=True)

    groups = [gm.group for gm in gms]

    return groups


# group suggestion
def get_group_suggestions(user):
    gms = GroupMember.objects.filter(member_name=get_user_name(user), is_joined=False)

    sug = [gm.group for gm in gms]

    return sug


# group member suggestion
def get_member_suggestions(user, groupid):
    if groupid == -2:
        return None
    gmout = []
    gmin = []
    ls = Link.objects.filter(group__id=groupid, creator=user)

    for l in ls:
        if l.from_member not in gmin or l.to_member not in gmin:
            gmin.append(l.from_member)
            gmin.append(l.to_member)

    for gm in GroupMember.objects.filter(group__id=groupid).exclude(user=user):
        if gm not in gmin:
            gmout.append(gm)

    return gmout


def get_group_joined_num(group):
    total = GroupMember.objects.filter(group=group).count()

    joined = GroupMember.objects.filter(group=group, is_joined=True).count()

    return str(joined)+'/'+str(total)


def create_user(name, email, password, password2):
    if user_existed(name):
        return 1
    elif not validate_email(email):
        return 2
    elif not validate_passwd(password, password2):
        return 3
    else:
        try:
            u = User.objects.create_user(name, email, password)
            u.save()
            pri = Privacy(link_me=True, see_my_global=True)
            pri.save()
            extra = Extra(user=u,
                          sex=False,
                          birth=datetime.date.today(),
                          credits=30,
                          privacy=pri)

            extra.save()
        except Exception, e:
            print 'user: ', e
            return 4
        return 0


def create_group(request, name, maxsize, identifier, type):
    u = request.user
    now = datetime.datetime.now()

    # need improved
    if group_name_existed(name) or maxsize > GROUP_MAXSIZE or u.extra.credits < GROUP_CREATED_CREDITS_COST:
        return 1
    try:

        g = Group(group_name=name,
                  creator=u,
                  type=type,
                  maxsize=maxsize,
                  identifier=identifier,
                  created_time=now,
                  deprecated=False)
        g.save()

        m = GroupMember(group=g,
                        user=u,
                        member_name=get_user_name(u),
                        token="creator",
                        is_creator=True,
                        is_joined=True,
                        created_time=now,
                        joined_time=now)

        u.extra.credits -= GROUP_CREATED_CREDITS_COST

        c = Credits(user=u,

                    action=-GROUP_CREATED_CREDITS_COST,
                    timestamp=now)

        m.save()
        u.save()
        c.save()

    except Exception, e:
        print 'group: ', e
        return 1

    # create dummy members
    create_dummy_members(g, u, 20)

    # create dummy links
    create_dummy_links(g, u, now)
    return 0


def create_group_member(group, name, identifier):

    now = datetime.datetime.now()

    if GroupMember.objects.filter(group=group, token=identifier).exists():
        return 1

    try:
        m = GroupMember(group=group,
                        member_name=name,
                        token=identifier,
                        is_creator=False,
                        is_joined=False,
                        created_time=now)
        m.save()
    except Exception, e:
        print 'group member: ', e
        return 1
    return 0


# -----
def member_join(user, group, identifier):
    now = datetime.datetime.now()

    m = GroupMember.objects.get(group=group, member_name=user.username, token=identifier)
    m.is_joined = True
    m.user = user
    m.joined_time = now
    m.save()
    return 0


def create_dummy_members(group, u, num):
    for i in range(num):
        if u.username != 'test'+str(i):
            create_group_member(group, 'test'+str(i), 'test'+str(i)+'@123.com')


def create_dummy_links(group, user, now):
    num = GroupMember.objects.filter(group=group).count()
    G = nx.barabasi_albert_graph(num, 2)

    i = 0
    for node in G.nodes():
        if node == 0:
            G.node[node]['name'] = user.username
        else:
            G.node[node]['name'] = 'test'+str(i)
            i += 1

    for (f, t) in G.edges():
        link = Link(creator=user,
                    from_member=GroupMember.objects.get(member_name=G.node[f]['name'], group=group),
                    to_member=GroupMember.objects.get(member_name=G.node[t]['name'], group=group),
                    group=group,
                    status=0,
                    created_time=now)
        link.save()


def group_name_existed(name):
    if Group.objects.filter(group_name=name).exists():
        return True
    return False


def check_groupid(id):
    if id == '':
        return -2
    if Group.objects.filter(id=id).exists():
        return id
    return 0


def user_existed(name):
    if User.objects.filter(username=name).exists():
        return True
    return False


def validate_email(email):
    if User.objects.filter(email=email).exists():
        return False
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) is not None:
            return True

    return False


def validate_passwd(password, password2):
    if len(password) < 6 or password != password2:

        return False

    return True



