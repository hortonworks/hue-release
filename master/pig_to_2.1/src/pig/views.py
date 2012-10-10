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

from pig.models import PigScript, Logs, UDF
from django.contrib.auth.models import User
from CommandPy import CommandPy
from PigShell import PigShell
from filebrowser.forms import UploadForm
from filebrowser.views import _upload, _massage_stats


class PigScriptForm(forms.Form):
    title = forms.CharField(max_length=100, required=False)
    text = forms.CharField(widget=forms.Textarea, required=False)

class UDFForm(forms.Form):
    UDF = forms.FileField(required=False)

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
    udfs = UDF.objects.filter(owner=request.user)
    udf_form = UploadForm()
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
                pig = CommandPy('pig %s' % script_path, LogModel=Logs)
                text = pig.returnCode()

            if request.POST.get('submit') in ['Explain', 'Describe',
                                              'Dump', 'Illustrate']:
                command = request.POST.get('submit').upper()
                limit = request.POST.get('limit') or 0
                pig = PigShell('pig %s' % script_path, LogModel=Logs)
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
                                                    text=text, udfs=udfs,
                                                    udf_form = udf_form))

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


def piggybank(request, obj_id):
    import posixpath
    from desktop.lib.exceptions import PopupException
    from django.utils.translation import ugettext as _

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():
            uploaded_file = request.FILES['hdfs_file']
            dest = form.cleaned_data['dest']
            print dest
            if request.fs.isdir(dest) and posixpath.sep in uploaded_file.name:
                raise PopupException(_('Sorry, no "%(sep)s" in the filename %(name)s.' % {'sep': posixpath.sep, 'name': uploaded_file.name}))

            dest = request.fs.join(dest, uploaded_file.name)
            tmp_file = uploaded_file.get_temp_path()
            username = request.user.username

            try:
                # Temp file is created by superuser. Chown the file.
                request.fs.do_as_superuser(request.fs.chmod, tmp_file, 0644)
                request.fs.do_as_superuser(request.fs.chown, tmp_file, username, username)

                # Move the file to where it belongs
                request.fs.rename(uploaded_file.get_temp_path(), dest)
            except IOError, ex:
                already_exists = False
                try:
                    already_exists = request.fs.exists(dest)
                except Exception:
                    pass
                if already_exists:
                    msg = _('Destination %(name)s already exists.' % {'name': dest})
                else:
                    msg = _('Copy to "%(name)s failed: %(error)s') % {'name': dest, 'error': ex}
                raise PopupException(msg)

            UDF.objects.create(url=dest, file_name=uploaded_file.name,
                               owner=request.user, description='111')
            return redirect(one_script, obj_id)

            # return {
            #     'status': 0,
            #     'path': dest,
            #     'result': _massage_stats(request, request.fs.stats(dest)),
            #     'next': request.GET.get("next")}
        else:
            raise PopupException(_("Error in upload form: %s") % (form.errors, ))

#    if request.method == 'POST':
#        form = UDFForm(request.POST, request.FILES)

#        if form.is_valid():
#            f = form.cleaned_data['UDF']
#            text = f.file.read()
#            script_path = 'piggybank/%s' % f.name
#            dirname = os.path.dirname(script_path)
#            try:
#                os.stat(dirname)
#            except:
#                os.mkdir(dirname)
#            f1 = open(script_path, 'w+b')
#            f1.write(text)
#            f1.close()
#            UDF.objects.create(url=script_path, file_name=f.name,
#                               owner=request.user, description='111')
#            return redirect(one_script, obj_id)
