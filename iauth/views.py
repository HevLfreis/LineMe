import datetime

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from LineMe.constants import PROJECT_NAME
from LineMe.settings import logger, DEPLOYED_LANGUAGE
from LineMe.utils import logger_join, md5
from LineMe.validations import validate_passwd, validate_email_for_reset
from friendnet.methods.basic.user import create_user
from iauth.forms import LoginForm, RegisterForm
from iauth.methods.session import get_session_id
from iauth.methods.utils import login_user, rt_existed, send_reset_passwd_email
from iauth.models import ResetToken

lang = DEPLOYED_LANGUAGE
if lang == 'zh-cn':
    template_dir = 'auth/zh_cn/'
else:
    template_dir = 'auth/'


def i_login(request):

    if request.user.is_authenticated():
        return redirect('home')

    context = {"project_name": PROJECT_NAME,
               "lang": lang,
               "status": ''}

    if request.method == 'GET':
        return render(request, template_dir+'login.html', context)

    elif request.method == 'POST':
        lf = LoginForm(request.POST)

        if lf.is_valid():
            if login_user(request, lf.cleaned_data['username'], lf.cleaned_data['password']):
                logger.info(logger_join('Login', get_session_id(request)))

                return redirect('home')

        context["status"] = -1
        return render(request, template_dir+'login.html', context)

    else:
        return HttpResponse(status=403)


def i_logout(request):
    logger.info(logger_join('Logout', get_session_id(request)))
    logout(request)
    return redirect('login')


def i_register(request):

    context = {"project_name": PROJECT_NAME,
               "lang": lang,
               "status": 0}

    if request.method == 'GET':
        return render(request, template_dir+'register.html', context)

    elif request.method == 'POST':
        rf = RegisterForm(request.POST)

        if rf.is_valid():

            status = create_user(request, rf.cleaned_register())
            context["status"] = status

            if status == 0:
                request.session['new_login'] = True
                return redirect('profile')

            else:
                return render(request, template_dir+'register.html', context)

        else:
            context["status"] = -4
            return render(request, template_dir+'register.html', context)

    else:
        return HttpResponse(status=403)


def reset(request):
    logger.info(logger_join('Access', get_session_id(request)))

    user = request.user

    if request.is_ajax():

        passwd = request.POST.get('old')
        new_passwd = request.POST.get('new')
        new_passwd2 = request.POST.get('new2')

        if user.check_password(passwd):
            if validate_passwd(new_passwd, new_passwd2):
                user.set_password(new_passwd)
                user.save()

                logger.info(logger_join('Reset', get_session_id(request)))
                logger.info(logger_join('Logout', get_session_id(request)))
                logout(request)

                return HttpResponse(0, content_type='text/plain')

        return HttpResponse(-1, content_type='text/plain')

    else:
        return HttpResponse(status=403)


def forget(request):

    if request.user.is_authenticated():
        return redirect('home')

    context = {"project_name": PROJECT_NAME,
               "lang": lang,
               "status": 0}

    if request.method == 'GET':
        return render(request, template_dir+'forget.html', context)

    elif request.method == 'POST':

        email = request.POST.get('email')

        if not validate_email_for_reset(email):

            context["status"] = -1
            return render(request, template_dir+'forget.html', context)

        user = User.objects.get(email=email)

        now = timezone.now()
        # if ResetToken.objects.filter(user=user, expired__gt=now).exists():
        #     token = ResetToken.objects.get(user=user).token
        # else:
        expired = now + datetime.timedelta(minutes=30)
        token = md5((user.username+str(expired)))

        reset_token = ResetToken(user=user,
                                 token=token,
                                 expired=expired)

        reset_token.save()

        href = 'https://lime.seeleit.com/resetbyemail/'+token

        try:
            send_reset_passwd_email(email, href)
        except Exception, e:
            logger.error(logger_join('Forget', email, e=e))
            context['status'] = -2
            return render(request, template_dir+'forget.html', context)

        context['status'] = 1
        return render(request, template_dir+'forget.html', context)

    else:
        return HttpResponse(status=403)


def reset_by_email(request, token):

    if request.user.is_authenticated():
        return redirect('home')

    context = {"project_name": PROJECT_NAME,
               "lang": lang,
               "status": 0}

    now = timezone.now()

    if request.method == 'GET' and rt_existed(token, now):
        return render(request, template_dir+'reset.html', context)

    elif request.method == 'POST' and rt_existed(token, now):

        rt = ResetToken.objects.get(token=token)

        user = rt.user
        new_passwd = request.POST.get('new')
        new_passwd2 = request.POST.get('new2')

        if validate_passwd(new_passwd, new_passwd2):
            user.set_password(new_passwd)
            user.save()

            rt.completed = True
            rt.save()

            logger.info(logger_join('Reset', get_session_id(request), u=user.username))

            context["status"] = 2
            return render(request, template_dir+'forget.html', context)

        else:
            # passwd is invalid
            context["status"] = -1
            return render(request, template_dir+'reset.html', context)

    else:
        # token expired or not existed
        context['status'] = -3
        return render(request, template_dir+'forget.html', context)



