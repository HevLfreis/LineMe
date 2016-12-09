from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from LineMe.constants import PROJECT_NAME
from LineMe.settings import DEPLOYED_LANGUAGE, logger
from LineMe.utils import get_template_dir, logger_join
from friendnet.methods.algorithm.recommender import Recommender
from friendnet.methods.basic.group import get_user_groups, group_privacy_check
from friendnet.methods.basic.user import get_user_msgs_count
from friendnet.models import Group
from iauth.methods.session import get_session_id

lang = DEPLOYED_LANGUAGE
template_dir = get_template_dir('question')


@login_required
def question(request, groupid=0):
    logger.info(logger_join('Access', get_session_id(request), gid=groupid))

    user = request.user
    groups = get_user_groups(user)
    rcmd_groups = Recommender(user).group()
    msgs_count = get_user_msgs_count(user)

    group = get_object_or_404(Group, id=groupid)

    group_privacy_check(user, group)

    context = {"project_name": PROJECT_NAME,
               "lang": lang,
               "user": user,
               "group": group,
               "groups": groups,
               "rcmd_groups": rcmd_groups,
               "msgs_count": msgs_count}

    return render(request, template_dir+'question.html', context)
