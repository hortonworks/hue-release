## Licensed to the Apache Software Foundation (ASF) under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  The ASF licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing,
## software distributed under the License is distributed on an
## "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
## KIND, either express or implied.  See the License for the
## specific language governing permissions and limitations
## under the License.

from desktop.lib.django_util import render

import os
from datetime import date, datetime

#from django.test.client import Client
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
#from django.core.files.uploadedfile import SimpleUploadedFile
#from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.mail import send_mail
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.conf import settings
from django import forms

from pig.models import PigScript, Logs
from django.contrib.auth.models import User
from CommandPy import CommandPy
from PigShell import PigShell

class PigScriptForm(forms.Form):
    title = forms.CharField(max_length=100, required=False)
    text = forms.CharField(widget=forms.Textarea, required=False)


def index(request):
    pig_script = PigScript.objects.filter(creater=request.user)
    return render('index.mako', request, dict(pig_script = pig_script))

def new_script(request, text = False):
    pig_script = PigScript.objects.filter(creater=request.user)

    form = PigScriptForm()
    if request.method == 'POST':
        form = PigScriptForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data['creater'] = request.user
            ps = PigScript.objects.create(**data)
            return redirect(one_script, ps.id)

    return render('new_script.mako', request, dict(form = form, pig_script = pig_script, text = text))


def one_script(request, obj_id, text = False):
    pig_script = PigScript.objects.filter(creater=request.user)
    instance = PigScript.objects.filter(id=obj_id)
    if request.method == 'POST':
        form = PigScriptForm(request.POST)
        if form.is_valid():
            instance.update(**form.cleaned_data)
            user = request.user
            script_path = 'pig_scripts/%s.pig' % instance[0].title
            dir = os.path.dirname(script_path)
            try:
                os.stat(dir)
            except:
                os.mkdir(dir)
            f1 = open(script_path, 'w')
            f1.write(instance[0].text)
            f1.close()

            start = datetime.now()
            if request.POST.get('submit') == 'Execute':
                pig = CommandPy('pig -x local %s' % script_path, LogModel=Logs)
                text = pig.returnCode()

            if request.POST.get('submit') in ['Explain', 'Describe',
                                              'Dump', 'Illustrate']:
                command = request.POST.get('submit').upper()
                limit = request.POST.get('limit') or 0
                pig = PigShell('pig -x local %s' % script_path, LogModel=Logs)
                text = pig.ShowCommands(command=command,
                                        limit=int(limit)) or pig.last_error
            finish = datetime.now()

            request.POST.get('email') == 'checked' and send_email(start, finish,
                                                                  instance[0].text,
                                                                  user, text)

    form = PigScriptForm(instance.values('title', 'text')[0])
    return render('edit_script.mako', request, dict(form=form,
                                                    instance=instance[0],
                                                    pig_script=pig_script,
                                                    text=text))

def delete(request, obj_id):
    pig_script = PigScript.objects.all().order_by('id')[0]
    instance = PigScript.objects.get(id=obj_id)
    text = instance.title + ' Deleted'
    instance.delete()
#    return index(request, text = text)
    return redirect(one_script, pig_script.id)

def send_email(start, finish, query, user, result):
    subject = 'Query result'
    message = render_to_string('mail/approved.html',
                               {'user': user, 'query': query, 'start': start,
                                'finish': finish, 'result': result})
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [user.email])
    
def show_logs(request):
    return render('logs.mako', request, dict(logs=Logs.objects.all()))
    
def script_clone(request, obj_id):
    pig_script = PigScript.objects.filter(id=obj_id).values()[0]
    check = 0
    if '(copy)' in pig_script['title'] or PigScript.objects.filter(title__icontains=pig_script['title'] + '(copy)'):
        check = PigScript.objects.filter(title__icontains=pig_script['title'])
    if check:
        p1 = check[0]
    else:
        pig_script['title'] = pig_script['title'] + '(copy)'
        del pig_script['id']
        del pig_script['date_created']
        p1 = PigScript.objects.create(**pig_script)
    return redirect(one_script, p1.id)
