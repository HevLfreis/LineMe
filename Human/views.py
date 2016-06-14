import base64
import cStringIO
import json
import os
import random
import datetime

from PIL import Image
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import Context

from Human.constants import PROJECT_NAME, STATIC_FOLDER, IDENTIFIER
from Human.forms import LoginForm, RegisterForm, GroupCreateForm, GroupMemberCreateForm, ReJoinIdentifierForm, \
    FileUploadForm
from Human.methods import create_user, get_user_groups, get_group_joined_num, check_groupid, \
    create_group, create_group_member, group_recommender, get_user_name, member_join, member_recommender, update_links, \
    link_confirm, link_reject, get_user_msgs, get_user_msgs_count, check_profile, get_user_invs, get_user_ego_graph, \
    get_user_global_info, get_user_global_graph
from Human.models import Group, GroupMember, Link, Extra
from Human.utils import create_avatar


def redirect2main(request):
    return redirect('home')


########################################################################

def lm_login(request):
    context = Context({"project_name": PROJECT_NAME, "status": ''})
    if request.method == 'POST':
        lf = LoginForm(request.POST)

        if lf.is_valid():
            username = lf.cleaned_data['username']
            password = lf.cleaned_data['password']
            print 'Login: ', username, password
            try:
                u = User.objects.get(username=username)
            except User.DoesNotExist:
                context["status"] = 'User does not existed'
                return render(request, 'Human/login.html', context)

            user = authenticate(username=username, password=password)
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
            return redirect('login')

    else:
        return render(request, 'Human/login.html', context)


def lm_logout(request):
    request.session.flush()
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
            name = rf.cleaned_data['username']
            email = rf.cleaned_data['email']
            password = rf.cleaned_data['password']
            password2 = rf.cleaned_data['password2']

            # status = 0
            status = create_user(name, email, password, password2)
            context["status"] = status
            # print name, password, email

            if status == 0:
                print 'New user created: ', name
                user = authenticate(username=name, password=password)
                if user is not None:
                    if user.is_active:
                        request.session['newUser'] = True
                        login(request, user)
                        return redirect('profile')
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
                return redirect('group', groupid=groupid)
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

        msg_creators = {xp: GroupMember.objects.get(user=xp.creator, group=xp.group).member_name for xp in p}
        # print msg_creators

        return render(request, 'Human/home_msg.html', {'msgs': p, 'my_members': my_members, 'msg_creators': msg_creators})
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


@login_required
def inv_panel(request, page):
    user = request.user
    if request.is_ajax():

        group_name = request.GET.get('groupname')
        if group_name:
            invs = get_user_invs(user, group_name)
        else:
            invs = get_user_invs(user)

        paginator = Paginator(invs, 8)

        try:
            p = paginator.page(page)
        except PageNotAnInteger:
            p = paginator.page(1)
        except EmptyPage:
            p = paginator.page(paginator.num_pages)

        my_members = GroupMember.objects.filter(user=user)

        return render(request, 'Human/home_inv.html', {'invs': p, 'my_members': my_members})
    else:
        raise Http404


@login_required
def send_email2unconfirmed(request):
    return 0


########################################################################

@login_required
def ego_network(request, groupid=0):
    user = request.user
    groups = get_user_groups(user)
    rcmd_groups = group_recommender(user)
    msgs_count = get_user_msgs_count(user)

    groupid = check_groupid(groupid)
    if groupid == 0:
        group = None
    else:
        group = get_object_or_404(Group, id=groupid)

    context = Context({"project_name": PROJECT_NAME, "user": user, "groups": groups,
                       "group": group, "rcmd_groups": rcmd_groups, "msgs_count": msgs_count})

    return render(request, 'Human/ego.html', context)


@login_required
def ego_graph(request, groupid=0):
    user = request.user
    if groupid == 0:
        return JsonResponse({"nodes": None, "links": None}, safe=False)

    print "Graph groupid: ", groupid

    data = get_user_ego_graph(user, groupid)

    return JsonResponse(data, safe=False)


@login_required
def rcmd_panel(request, groupid, page):
    user = request.user
    if request.is_ajax():
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
        new_links = request.POST.get('links')
        update_links(new_links, groupid, user)
        return HttpResponse("Link update successfully")

    else:
        raise Http404


########################################################################

@login_required
def global_network(request, groupid=0):
    user = request.user
    groups = get_user_groups(user)

    msgs_count = get_user_msgs_count(user)

    groupid = check_groupid(groupid)
    context = Context()

    if groupid == 0:
        group = None
    else:
        group = get_object_or_404(Group, id=groupid)
        context.push(get_user_global_info(user, groupid))

    context.push({"project_name": PROJECT_NAME, "user": user, "groups": groups,
                  "group": group, "msgs_count": msgs_count})

    return render(request, 'Human/global.html', context)


@login_required
def global_graph(request, groupid=0):
    user = request.user
    if groupid == 0:
        return JsonResponse({"nodes": None, "links": None}, safe=False)

    print "Graph groupid: ", groupid

    data = get_user_global_graph(user, groupid)

    return JsonResponse(data, safe=False)


########################################################################

@login_required
def profile(request):
    user = request.user
    first_login = request.session.get('newUser')

    username = get_user_name(user)

    msgs_count = get_user_msgs_count(user)

    context = Context({"project_name": PROJECT_NAME, "user": user, "username": username, "msgs_count": msgs_count,
                       "first_login": first_login})

    if request.is_ajax():
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        birth = request.POST.get('birth')
        sex = int(request.POST.get('sex'))
        country = request.POST.get('country')
        city = request.POST.get('city')
        institution = request.POST.get('institution')

        if check_profile(first_name, last_name, birth, sex, country, city, institution):

            try:
                user.first_name = first_name
                user.last_name = last_name

                ue = Extra.objects.get(user=user)
                ue.sex = sex
                ue.birth = datetime.datetime.strptime(birth, '%Y/%m/%d').date()
                # ue.location = country+' '+city
                ue.institution = institution
                user.save()
                ue.save()

            except Exception, e:
                print 'Profile update failed: ', e
                return HttpResponse(-1)

            print 'Update profile: user:', user.id, first_name, last_name, birth, country, city, institution, sex
            if first_login:
                create_avatar(user.id, username=first_name+' '+last_name)
                del request.session['newUser']

            return HttpResponse(0)

        else:
            return HttpResponse(-1)

    return render(request, 'Human/profile.html', context)


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
            image.resize((200, 200)).save(path+str(userid)+".png", image.format, quality=100)
            # print image.format, image.size, image.mode
        except Exception, e:
            print 'Avatar: ', e
            return HttpResponse('Upload failed')

        return HttpResponse('Upload success')
    else:
        raise Http404


########################################################################


@login_required
def manage_group(request, groupid, page=1):
    user = request.user

    upfile = request.session.get('upfile')

    groups = get_user_groups(user)
    rcmd_groups = group_recommender(user)

    msgs_count = get_user_msgs_count(user)

    # groupid = request.GET.get('groupid')
    group = Group.objects.get(id=groupid)

    context = Context({"project_name": PROJECT_NAME, "user": user, "group": group, "groups": groups,
                       "rcmd_groups": rcmd_groups, "upfile": upfile, "msgs_count": msgs_count})

    if upfile:
        del request.session['upfile']

    if groupid != check_groupid(groupid):
        raise Http404

    if request.method == 'POST':
        gf = GroupMemberCreateForm(request.POST)
        # print gf.is_valid()
        if gf.is_valid():
            name = gf.cleaned_data['name']
            identifier = gf.cleaned_data['identifier']

            # ---------------------------------------dangerous
            status = create_group_member(group, name, identifier)
            if status == 0:
                print 'New group member created: ', name, identifier
            return redirect('group', groupid=groupid)

    joined = request.session.get('joined')

    context.push(joined=joined)
    if joined:
        del request.session['joined']

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
        # page = 1 if request.GET.get('page') is None else request.GET.get('page')
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
def join(request, groupid):

    user = request.user
    if request.is_ajax():
        # groupid = int(request.POST.get('groupid'))
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
            # groupid = int(rf.cleaned_data['groupid'])
            group = Group.objects.get(id=groupid)
            identifier = rf.cleaned_data['identifier']
            print 'Rejoin: ', groupid, identifier
            if identifier != '':
                if GroupMember.objects.filter(group=group, member_name=get_user_name(user), token=identifier).exists():
                    member_join(user, group, identifier)

                    return redirect('group', groupid=groupid)

        # -----
        request.session['joined'] = True
        return redirect('group', groupid=groupid)

    else:
        raise Http404


@login_required
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
                            return redirect('group', groupid=groupid)
                        else:
                            members.append(kv)

                for m in members:
                    if create_group_member(group, m[0], m[1]) != 0:

                        return redirect('group', groupid=groupid)
                request.session['upfile'] = True
                return redirect('group', groupid=groupid)
            else:

                return redirect('group', groupid=groupid)

    else:

        return redirect('group', groupid=groupid)



