from djangomako.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect, render
from django.http import HttpResponse, Http404
from django.core.servers.basehttp import FileWrapper

from models import UserLocation
import settings
import userinfo

import os
import time
import string
from urlparse import urlparse
import mimetypes

def landing(request):
    if userinfo.load_info() or not settings.REQUIRE_REGISTRATION or \
        userinfo.is_skipped():
        landing_index = os.path.join(settings.LANDING_PATH, 'index.html')

        rfile = landing_index
        response = HttpResponse(FileWrapper(file(rfile, 'rb')),
                                mimetype=mimetypes.guess_type(rfile)[0])

        return response
    else:
        return redirect('/register')

def csrf_token(context):
    csrf_token = context.get('csrf_token', '')
    if csrf_token == 'NOTPROVIDED':
        return ''
    return u'<div style="display:none"><input type="hidden" name="csrfmiddlewaretoken" value="%s" /></div>' % (csrf_token)

def register(request):
    #Registration form
    skip_file = settings.USERINFO_FILE_PATH + ".skip"
    if os.path.exists(skip_file):
        os.remove(skip_file)
    
    if request.method == 'POST':
        form = userinfo.RegistrationForm(request.POST)
        if form.is_valid():
            userinfo.save(form.cleaned_data)
            return redirect('/')
    else:
        if userinfo.load_info():
            return redirect('/')

        form = userinfo.RegistrationForm()

    from django.core.context_processors import csrf

    return render_to_response("registration.html",
                {'form': form,
                 'csrf': csrf_token(RequestContext(request))},
                 context_instance=RequestContext(request))


def register_skip(request):
    with file(settings.USERINFO_FILE_PATH + ".skip", "w") as f:
        f.write("")
    return redirect('/')


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
