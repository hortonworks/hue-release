from djangomako.shortcuts import render_to_response
from django.shortcuts import redirect
from django.http import HttpResponse, Http404

from models import UserLocation

import settings

import os
import time
import string
from urlparse import urlparse


def landing(request):
    #Needs symbolic link from templates to landing-page folder
    return render_to_response("landing/index.html", {})

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
