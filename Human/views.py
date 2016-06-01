import base64
import cStringIO
import json
import os
import random
from PIL import Image
import datetime
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, render_to_response, redirect, get_object_or_404, get_list_or_404
from django.template import Context
from django.utils import timezone
from Human.constants import PROJECT_NAME, STATIC_FOLDER, IDENTIFIER
from Human.forms import LoginForm, RegisterForm, GroupCreateForm, GroupMemberCreateForm, ReJoinIdentifierForm, \
    FileUploadForm
from Human.methods import create_user, get_user_groups, get_group_joined_num, check_groupid, \
    create_group, create_group_member, group_recommender, get_user_name, member_join, member_recommender, update_links, \
    link_confirm, link_reject, get_user_msgs, get_user_msgs_count
from Human.models import Group, GroupMember, Link


def redirect2main(request):
    return redirect('home')


########################################################################

def lm_login(request):
    context = Context({"project_name": PROJECT_NAME, "status": ''})
    if request.method == 'POST':
        lf = LoginForm(request.POST)

        if lf.is_valid():
            email = lf.cleaned_data['email']
            password = lf.cleaned_data['password']
            print 'Login: ', email, password
            try:
                u = User.objects.get(email=email)
            except User.DoesNotExist:
                context["status"] = 'User does not existed'
                return render(request, 'Human/login.html', context)

            user = authenticate(username=u.username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('home')
                else:
                    return redirect('login')
            else:
                context["status"] = 'User does not existed'
                return render(request, 'Human/login.html', context)
        else:
            render(request, 'Human/login.html', context)

    else:
        return render(request, 'Human/login.html', context)


def lm_logout(request):
    logout(request)
    return redirect('login')


def lm_register(request):

    # status 0 :
    # status 1 : wrong name
    # status 2 : wrong email
    # status 3 : wrong password
    context = Context({"project_name": PROJECT_NAME, "status": 0})
    if request.method == 'POST':
        rf = RegisterForm(request.POST)
        # print 'Register Form valid: ', rf.is_valid()
        if rf.is_valid():
            name = rf.cleaned_data['name']
            email = rf.cleaned_data['email']
            password = rf.cleaned_data['password']
            password2 = rf.cleaned_data['password2']

            status = 0
            status = create_user(name, email, password, password2)
            context["status"] = status
            # print name, password, email

            if status == 0:
                print 'New user created: ', name
                user = authenticate(username=name, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return redirect('home')
                    else:
                        return redirect('register')
                else:
                    return redirect('register')
            else:
                return render(request, 'Human/register.html', context)
        else:
            return render(request, 'Human/register.html', context)

    else:
        return render(request, 'Human/register.html', context)


########################################################################

@login_required
def home(request):
    user = request.user
    groups = get_user_groups(user)
    my_groups, in_groups = {}, {}

    for group in groups:
        if group.creator == user:
            my_groups.setdefault(group, get_group_joined_num(group))
        else:
            in_groups.setdefault(group, get_group_joined_num(group))

    msgs_count = get_user_msgs_count(user)
    rcmd_groups = group_recommender(user)

    context = Context({"project_name": PROJECT_NAME, "user": user, "my_groups": my_groups,
                       "in_groups": in_groups, "rcmd_groups": rcmd_groups, "msgs_count": msgs_count,
                       "status": 0, "identifier": IDENTIFIER})

    if request.method == 'POST':
        gf = GroupCreateForm(request.POST)
        # print gf.is_valid()
        if gf.is_valid():
            name = gf.cleaned_data['name']
            maxsize = gf.cleaned_data['maxsize']
            identifier = int(gf.cleaned_data['identifier'])
            type = int(gf.cleaned_data['type'])
            print 'New group request: ', name, maxsize, identifier, type
            status = create_group(request, name, maxsize, identifier, type)
            context["status"] = status
            if status == 0:
                print 'New group created: ', name, maxsize, identifier, type

                groupid = Group.objects.get(group_name=name).id
                return redirect('/group?groupid='+str(groupid))
            else:
                return render(request, 'Human/home.html', context)
        else:
            context["status"] = 1
            return render(request, 'Human/home.html', context)
    else:
        return render(request, 'Human/home.html', context)


@login_required
def msg_panel(request, page):
    user = request.user
    if request.is_ajax():

        msgs = get_user_msgs(user)

        paginator = Paginator(msgs, 10)

        try:
            p = paginator.page(page)
        except PageNotAnInteger:
            p = paginator.page(1)
        except EmptyPage:
            p = paginator.page(paginator.num_pages)

        my_members = GroupMember.objects.filter(user=user)

        return render(request, 'Human/home_msg.html', {'msgs': p, 'my_members': my_members})
    else:
        raise Http404


@login_required
def msg_handle(request, type, linkid):
    user = request.user
    if type == '1':
        status = link_confirm(user, int(linkid))
        print 'Confirm Link: ', linkid, user.username
    elif type == '0':
        status = link_reject(user, int(linkid))
        print 'Reject Link: ', linkid, user.username
    else:
        raise Http404

    return HttpResponse(status)


########################################################################

@login_required
def ego(request):
    user = request.user
    groups = get_user_groups(user)
    rcmd_groups = group_recommender(user)
    msgs_count = get_user_msgs_count(user)

    groupid = check_groupid(request.GET.get('groupid'))
    if groupid == 0:
        group = None
    else:
        group = get_object_or_404(Group, id=groupid)

    context = Context({"project_name": PROJECT_NAME, "user": user, "groups": groups,
                       "group": group, "rcmd_groups": rcmd_groups, "status": 0, "msgs_count": msgs_count})

    return render(request, 'Human/ego.html', context)


@login_required
def graph(request, groupid):
    user = request.user
    if groupid == '0':
        return HttpResponse(json.dumps({"nodes": None, "links": None}))

    print "Graph groupid: ", groupid

    gms = []
    ls = Link.objects.filter(group__id=groupid, creator=user)

    data = {}
    nodes, links = [], []

    self = GroupMember.objects.get(group__id=groupid, user=user)
    nodes.append({'id': self.id, 'userid': self.user.id, 'name': self.member_name,
                  'self': True, 'group': 0})

    if ls.count() != 0:

        for link in ls:

            if link.source_member not in gms and link.source_member != self:
                gms.append(link.source_member)
            if link.target_member not in gms and link.target_member != self:
                gms.append(link.target_member)

        for gm in gms:
            nodes.append({'id': gm.id, 'userid': (-1 if gm.user is None else gm.user.id), 'name': gm.member_name,
                          'self': False, 'group': random.randint(1, 4)})

        for link in ls:
            links.append({'id': link.id, 'source': link.source_member.id, 'target': link.target_member.id,
                          'status': link.status, 'value': 1, 'group': link.group.id})

    data["nodes"] = nodes
    data["links"] = links

    return HttpResponse(json.dumps(data))


@login_required
def rcmd_panel(request, groupid, page):
    user = request.user
    if request.is_ajax():
        # groupid = check_groupid(request.GET.get('groupid'))
        if groupid == '0':
            return render(request, 'Human/ego_rcmd.html')

        rcmd_gms = member_recommender(user, groupid)

        paginator = Paginator(rcmd_gms, 6)

        try:
            p = paginator.page(page)
        except PageNotAnInteger:
            p = paginator.page(1)
        except EmptyPage:
            p = paginator.page(paginator.num_pages)

        return render(request, 'Human/ego_rcmd.html', {'members': p})
    else:
        raise Http404


@login_required
def update_graph(request, groupid):
    user = request.user
    if request.is_ajax():
        newLinks = request.POST.get('links')
        update_links(newLinks, groupid, user)
        return HttpResponse("Link update successfully")

    else:
        raise Http404


########################################################################

@login_required
def avatar(request):
    user = request.user
    msgs_count = get_user_msgs_count(user)

    context = Context({"project_name": PROJECT_NAME, "user": user, "msgs_count": msgs_count})
    return render(request, 'Human/avatar.html', context)


@login_required
def img_handle(request):
    if request.is_ajax():
        print 'Avatar ajax received: ', request.user.id
        userid = request.user.id
        try:

            image_string = cStringIO.StringIO(base64.b64decode(request.POST['imgBase64'].partition('base64,')[2]))
            image = Image.open(image_string)

            path = os.path.join(STATIC_FOLDER, 'images/user_avatars/')
            image.save(path+str(userid)+".png", image.format, quality=100)
            # print image.format, image.size, image.mode
        except Exception, e:
            print 'Avatar: ', e
            return HttpResponse('Upload failed')

        return HttpResponse('Upload success')
    else:
        raise Http404


########################################################################


@login_required
def manage_group(request):
    user = request.user

    up = request.GET.get('up')
    groups = get_user_groups(user)
    rcmd_groups = group_recommender(user)

    msgs_count = get_user_msgs_count(user)

    groupid = request.GET.get('groupid')
    group = Group.objects.get(id=groupid)

    context = Context({"project_name": PROJECT_NAME, "user": user, "group": group, "groups": groups,
                       "rcmd_groups": rcmd_groups, "up": up, "msgs_count": msgs_count})

    if groupid != check_groupid(groupid):
        raise Http404

    if request.method == 'POST':
        gf = GroupMemberCreateForm(request.POST)
        # print gf.is_valid()
        if gf.is_valid():
            name = gf.cleaned_data['name']
            identifier = gf.cleaned_data['identifier']

            # dangerous
            status = create_group_member(group, name, identifier)
            if status == 0:
                print 'New group member created: ', name, identifier
            return redirect('/group/?groupid='+str(groupid))

    joined = request.GET.get('joined')

    if joined == '0':
        context.push(joined=0)
    elif joined == '1':
        context.push(joined=1)

    if user != group.creator:
        members = GroupMember.objects.filter(group=group)
        members_count = members.count()

        # -----
        if GroupMember.objects.filter(group=group, user=user, is_joined=True).exists():
            is_member = True
        else:
            is_member = False
        context.push(creator=group.creator, members_count=members_count, is_member=is_member)
        return render(request, 'Human/group2.html', context)

    else:
        members = GroupMember.objects.filter(group=group)
        page = 1 if request.GET.get('page') is None else request.GET.get('page')
        paginator = Paginator(members, 15)

        try:
            p = paginator.page(page)
        except PageNotAnInteger:
            p = paginator.page(1)
        except EmptyPage:
            p = paginator.page(paginator.num_pages)

        context.push(members=p)
        members_count = members.count()
        context.push(creator=user,  members_count=members_count)
        return render(request, 'Human/group1.html', context)


@login_required
def join(request):

    user = request.user
    if request.is_ajax():
        groupid = int(request.POST.get('groupid'))
        identifier = request.POST.get('identifier')
        print 'Join:', groupid, identifier
        group = Group.objects.get(id=groupid)
        gm = GroupMember.objects.filter(group=group, member_name=get_user_name(user))
        if not gm.exists():
            return HttpResponse(-2)

        if group.identifier == 1:
            if gm.filter(token=user.email).exists():
                member_join(user, group, user.email)
                return HttpResponse(0)
            else:
                return HttpResponse(-1)
        elif group.identifier == 2:
            if gm.filter(token=user.institution).exists():
                member_join(user, group, user.institution)
                return HttpResponse(0)
            else:
                return HttpResponse(-1)
        elif group.identifier == 0:
            if gm.filter(token=identifier).exists():
                member_join(user, group, identifier)
                return HttpResponse(0)
            else:
                return HttpResponse(-1)
        else:
            return HttpResponse(-1)

    elif request.method == 'POST':
        rf = ReJoinIdentifierForm(request.POST)

        if rf.is_valid():
            groupid = int(rf.cleaned_data['groupid'])
            group = Group.objects.get(id=groupid)
            identifier = rf.cleaned_data['identifier']
            print 'Rejoin: ', groupid, identifier
            if identifier != '':
                if GroupMember.objects.filter(group=group, member_name=get_user_name(user), token=identifier).exists():
                    member_join(user, group, identifier)
                    return redirect('/group/?groupid='+str(groupid)+'&joined=0')

        # -----
        groupid = int(rf.cleaned_data['groupid'])
        return redirect('/group/?groupid='+str(groupid)+'&joined=1')

    else:
        raise Http404


def upload_members(request, groupid):
    user = request.user

    if Group.objects.filter(creator=user, id=groupid).exists():
        group = Group.objects.get(id=groupid)

        if request.method == 'POST':
            fuf = FileUploadForm(request.POST, request.FILES)
            if fuf.is_valid():
                members = []
                with request.FILES.get('members') as f:
                    for l in f:
                        kv = l.strip().split(',')

                        if len(kv) != 2:
                            return redirect('/group/?groupid='+str(groupid)+'&up=0')
                        else:
                            members.append(kv)

                for m in members:
                    if create_group_member(group, m[0], m[1]) != 0:
                        return redirect('/group/?groupid='+str(groupid)+'&up=0')

                return redirect('/group/?groupid='+str(groupid)+'&up=1')
            else:
                return redirect('/group/?groupid='+str(groupid)+'&up=0')

    else:
        return redirect('/group/?groupid='+str(groupid)+'&up=0')



