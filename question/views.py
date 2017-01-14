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
from methods import Questionnaire
from question.models import QuestionTemplate

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
    qt = QuestionTemplate.objects.get(group__id=groupid)

    context = {"project_name": PROJECT_NAME,
               "lang": lang,
               "user": user,
               "group": group,
               "groups": groups,
               "rcmd_groups": rcmd_groups,
               "msgs_count": msgs_count,
               "authenticated": qt.authenticated,
               "template": qt.template}

    return render(request, template_dir+'question.html', context)


@login_required
def question_handle(request, groupid):

    user = request.user

    if not Group.objects.filter(id=groupid, creator=user).exists():
        return HttpResponse(status=403)

    if request.is_ajax():
        try:
            qn = Questionnaire(groupid)
            qn.proceeding(request)
            qn.save()
        except Exception, e:
            print e

        return HttpResponse(0, content_type='text/plain')

    else:
        return HttpResponse(status=403)
