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
import simplejson as json

#from django.test.client import Client
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.models import User

from desktop.lib.exceptions import PopupException
from filebrowser.views import _do_newfile_save
from filebrowser.forms import UploadFileForm
from pig.models import PigScript, UDF, Job
from pig.templeton import Templeton
from pig.forms import PigScriptForm, UDFForm


def index(request, obj_id=None):
    result = {}
    if request.method == 'POST':
        form = PigScriptForm(request.POST)
        if not form.is_valid():
            raise PopupException(
                "".join(["%s: %s" % (field, error) for field, error in form.errors.iteritems()])
            )
        if request.POST.get("script_id"):
            instance = PigScript.objects.get(pk=request.POST['script_id'])
            form.instance = instance
            form.save()
        else:
            instance = PigScript(**form.cleaned_data)
            instance.user = request.user
            instance.saved = True
            instance.save()
            result['script_id'] = instance.pk
        return redirect("view_script", obj_id=instance.pk)
    if obj_id:
        instance = PigScript.objects.get(pk=obj_id)
        for field in instance._meta.fields:
            result[field.name] = getattr(instance, field.name)
    return render('edit_script.mako', request, dict(result=result))


def one_script(request, obj_id, text=False):
    pig_script = PigScript.objects.filter(user=request.user)
    instance = PigScript.objects.filter(id=obj_id)
    udfs = UDF.objects.filter(owner=request.user)
    udf_form = UploadFileForm()
    form = PigScriptForm(request.POST)
    if request.method == 'POST':
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

            if request.POST.get('submit') == 'Schedule':
                te = Templeton()
                statusdir = '/tmp/{u}{t}'.format(
                    u=request.user.username, t=datetime.now().strftime("%s"))
                job = te.pig_query(execute=instance[0].text, statusdir=statusdir)
                import time
                completed, i, f1_r = False, 0, 'oops'
                while not completed:
                    sleep_time = 5
                    time.sleep(sleep_time)
                    jobb = te.check_job(job['id'])
                    completed = jobb.get('completed')
                    i += 1
                    if i > 11:
                        break

                try:
                    f1 =request.fs.open(statusdir + "/stdout")
                    f1_r = f1.read()
                    f1.close()
                except:
                    f1 =request.fs.open(statusdir + "/stderr")
                    f1_r = f1.read()
                    f1.close()

                text = str(job) + '\n' + f1_r

            finish = datetime.now()
            request.POST.get('email') == 'checked' and send_email(start, finish,
                                                                  instance[0].text,
                                                                  user, text)

    form = PigScriptForm(instance.values('title', 'text')[0])
    return render('edit_script.mako', request, dict(form=form,
                                                    instance=instance[0],
                                                    pig_script=pig_script,
                                                    text=text, udfs=udfs,
                                                    result={},
                                                    udf_form = udf_form))

def delete(request, obj_id):
    instance = PigScript.objects.get(id=obj_id)
#    text = instance.title + ' Deleted'
    instance.delete()
#    return index(request, text = text)
    return redirect(index)

def send_email(start, finish, query, user, result):
    subject = 'Query result'
    message = render_to_string('mail/approved.html',
                               {'user': user, 'query': query, 'start': start,
                                'finish': finish, 'result': result})
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [user.email])


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


def piggybank(request, obj_id = False):
    import posixpath
    
    from django.utils.translation import ugettext as _

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

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
            if obj_id:
                return redirect(one_script, obj_id)
            else:
                return redirect(piggybank_index)

            # return {
            #     'status': 0,
            #     'path': dest,
            #     'result': _massage_stats(request, request.fs.stats(dest)),
            #     'next': request.GET.get("next")}
        else:
            raise PopupException(_("Error in upload form: %s") % (form.errors, ))

def piggybank_index(request):
    udfs = UDF.objects.filter(owner=request.user)
    pig_script = PigScript.objects.filter(user=request.user)
    udf_form = UploadFileForm()
    return render('piggybank_index.mako', request, dict(udfs=udfs, pig_script=pig_script, udf_form = udf_form))
    
def udf_del(request, obj_id):
    pig_script = PigScript.objects.filter(user=request.user)
    udf = UDF.objects.get(id=obj_id)
    udf.delete()
    return redirect(piggybank_index)


def start_job(request):
    t = Templeton(request.user.username)
    statusdir = "/tmp/.pigjobs/%s" % datetime.now().strftime("%s")
    script_file = statusdir + "/script.pig"
    #_do_newfile_save(request.fs, script_file, request.POST['pig_script'], "utf-8")
    #job = t.pig_query(pig_file=script_file, statusdir=statusdir)
    job = t.pig_query(execute=request.POST['pig_script'], statusdir=statusdir)

    if request.POST.get("script_id"):
        script = PigScript.objects.get(pk=request.POST['script_id'])
    else:
        script = PigScript(user=request.user, saved=False)
    script.pig_script = request.POST['pig_script']
    script.python_script = request.POST['python_script']
    script.save()
    job_object = Job.objects.create(job_id=job['id'],
                                    statusdir=statusdir,
                                    script=script,
                                    email_notification=bool(request.POST['email']))
    return HttpResponse(json.dumps(
        {"job_id": job['id'],
         "text": "The Job has been started successfully.\
         You can check job status on the following <a href='%s'>link</a>" % reverse("single_job", args=[job['id']])}))


def kill_job(request):
    t = Templeton(request.user.username)
    try:
        job_id = request.POST['job_id']
        t.kill_job(job_id)
        return HttpResponse(json.dumps({"text": "Job %s was killed" % job_id}))
    except:
        return HttpResponse(json.dumps({"text": "An error was occured"}))


def get_job_result(request):
    job = Job.objects.get(job_id=request.POST['job_id'])
    statusdir = job.statusdir
    result = {}
    try:
        error = request.fs.open(statusdir + "/stderr", "r")
        result['error'] = error.read()
        stdout = request.fs.open(statusdir + "/stdout", "r")
        result['stdout'] = stdout.read()
        exit_code = request.fs.open(statusdir + "/exit", "r")
        result['exit'] = exit_code.read()
        exit_code.close()
        stdout.close()
        error.close()
    except:
        result['error'] = ""
        result['stdout'] = ""
        result['exit'] = ""
    return HttpResponse(json.dumps(result))


def query_history(request):
    return render("query_history.mako", request, dict(jobs=Job.objects.all()))


def show_job_result(request, job_id):
    try:
        job = Job.objects.get(job_id=job_id)
    except:
        raise Http404("This job doesn't exist.'")
    statusdir = job.statusdir
    result = {}
    try:
        error = request.fs.open(statusdir + "/stderr", "r")
        result['error'] = error.read()
        stdout = request.fs.open(statusdir + "/stdout", "r")
        result['stdout'] = stdout.read()
        error.close()
        stdout.close()
        instance = job.script
        for field in instance._meta.fields:
            result[field.name] = getattr(instance, field.name)
    except:
        raise Http404("Script data has been deleted.")

    return render('edit_script.mako', request, dict(result=result))


def delete_job_object(request, job_id):
    try:
        job = Job.objects.get(job_id=job_id)
    except:
        raise Http404("This job doesn't exist.'")
    else:
        request.fs.rmtree(job.statusdir)
        job.delete()
    return HttpResponseRedirect(reverse("query_history"))



    