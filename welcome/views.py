from django.shortcuts import render

# Create your views here.
from LineMe.constants import PROJECT_NAME
from LineMe.settings import DEPLOYED_LANGUAGE
from LineMe.utils import get_template_dir

lang = DEPLOYED_LANGUAGE
template_dir = get_template_dir('welcome')


def welcome(request):

    if request.user.is_authenticated():
        login = True
    else:
        login = False

    context = {"project_name": PROJECT_NAME,
               "lang": lang,
               "login": login}

    return render(request, template_dir+'welcome.html', context)



