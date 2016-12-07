from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from LineMe.settings import DEPLOYED_LANGUAGE
from LineMe.utils import get_template_dir

lang = DEPLOYED_LANGUAGE
template_dir = get_template_dir('question')

@login_required
def question(request, groupid=0):
    return render(request, template_dir+'question.html')
