from djangomako.shortcuts import render_to_response
from django.shortcuts import redirect
from django.http import HttpResponse, Http404

from models import Section, Step, UserLocation, UserStep

import settings

import os
import time
import string
from urlparse import urlparse


def tutorials_last_url(tutorial_view):
    def save_user_location(request, *args):
        if request.user.is_authenticated() \
        and request.user.username != "AnonymousUser":
            user_location = UserLocation.objects.get_or_create(user=request.user)[0]
            user_location.step_location = request.build_absolute_uri()
            user_location.save()
        return tutorial_view(request, *args)
    return save_user_location


def landing(request):
    #Needs symbolic link from templates to landing-page folder
    return render_to_response("landing/index.html",
                    {'content' : location,
                     'step_location': step_location})

def tutorials(request):
    location = settings.CONTENT_FRAME_URL
    step_location = "/lesson/"
    if request.user.is_authenticated() \
        and request.user.username != "AnonymousUser":
        try:
            ustep = UserLocation.objects.get(user=request.user)
            hue_location = ustep.hue_location
            step_location = ustep.step_location
            if step_location == None:
                step_location = "/lesson/"
            if urlparse(hue_location).netloc==urlparse(location).netloc:
                location = hue_location
        except UserLocation.DoesNotExist:
            pass

    return render_to_response("lessons.html",
                    {'content' : location,
                     'step_location': step_location})

@tutorials_last_url
def lesson_list(request):
    sections = Section.objects.all()
    steps = map(
        lambda s: Step.objects.filter(section=s).order_by('order'), sections)
    now = int(time.time()) - 172800
    location = ''
    if request.user.is_authenticated() \
    and request.user.username != 'AnonymousUser':
        user_steps = [x.step for x in UserStep.objects.filter(user=request.user)]
        try:
            user_location = UserLocation.objects.get(user=request.user)
            location = user_location.hue_location
        except UserLocation.DoesNotExist:
            pass
    else:
        user_steps = {}

    return render_to_response("lesson_list.html", {'lessons': sections,
                              'steps': steps, 'now': now,
                              'user_steps': user_steps,
                              'x': request.user, 'loc': location})

@tutorials_last_url
def lesson(request, section_id, step_id):
    section = Section.objects.get(id=section_id)
    steps = Step.objects.filter(section=section).order_by('order')
    step = Step.objects.get(section=section, order=step_id)

    if request.user.is_authenticated() \
    and request.user.username != 'AnonymousUser':
        try:
            UserStep.objects.get(user=request.user, step=step)
        except UserStep.DoesNotExist:
            user_step = UserStep(user = request.user)
            user_step.save(using='default')
            user_step.step = step
            user_step.save(using='default')

    git_files = os.path.join(settings.PROJECT_PATH, 'run/git_files')
    filename = step.file_path

    html = string.join(file(os.path.join(git_files, filename)).readlines())
    return render_to_response("one_lesson.html", {'step': step,
                                                  'max': len(steps),
                                                  'step_html': html})


def lesson_steps(request, section_id, step=0):
    section = Section.objects.get(id=section_id)
    steps = Step.objects.filter(section=section).order_by('order')
    return render_to_response("lesson.html", {'steps': steps})


def content(request, page):
    if page == '':
        return redirect('/')
    return render_to_response("content.html", {})

def sync_location(request):
    if request.method == 'GET':
        if not request.user.is_authenticated() \
        or request.user.username == 'AnonymousUser':
            return HttpResponse('')

        hue_location = None
        if 'loc' in request.GET:
            hue_location = request.GET['loc']

        ustep = UserLocation.objects.get_or_create(user=request.user)[0]
        ustep.hue_location = hue_location
        ustep.save()

        return HttpResponse('')
    else:
        raise Http404

def lesson_static(request, section_id, step, path):
    import mimetypes
    from django.core.servers.basehttp import FileWrapper

    section = Section.objects.get(id=section_id)
    step = Step.objects.filter(section=section, order=step)[0]
    git_files = os.path.join(settings.PROJECT_PATH, 'run/git_files')
    filename = step.file_path

    static_path = "%s/%s" % ("/".join(filename.split('/')[:-1]), path)
    rfile = os.path.join(git_files, static_path)
    response = HttpResponse(FileWrapper(file(rfile, 'rb')),
                            mimetype=mimetypes.guess_type(rfile)[0])

    return response

def get_file(request, path):
    import mimetypes
    from django.core.servers.basehttp import FileWrapper

    git_files = os.path.join(settings.PROJECT_PATH, 'run/git_files')

    rfile = os.path.join(git_files, path)
    response = HttpResponse(FileWrapper(file(rfile, 'rb')),
                            mimetype=mimetypes.guess_type(rfile)[0])

    return response

def network_info(request):
    import subprocess
    commands = [
        "route -n",
        "getent ahosts",
        "ip addr",
        "cat /etc/resolv.conf",
        "cat /etc/hosts",
        "ps aux | grep java",
        "netstat -lnp",
        ]

    netinfo = dict((cmd, subprocess.check_output(cmd, shell=True))
                for cmd in commands)

    return render_to_response("netinfo.html", {'info': netinfo})
