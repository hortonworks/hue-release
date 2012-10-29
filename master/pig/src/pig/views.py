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
import os, re
import simplejson as json

from datetime import date, datetime
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.models import User

from desktop.lib.exceptions import PopupException
from desktop.lib.django_util import login_notrequired, render
from filebrowser.views import _do_newfile_save
from filebrowser.forms import UploadFileForm
from pig.models import PigScript, UDF, Job
from pig.templeton import Templeton
from pig.forms import PigScriptForm, UDFForm
from pig.CommandPy import CommandPy


def index(request, obj_id=None, pig_script=None):
    result = {}
    result['scripts'] = PigScript.objects.filter(saved=True, user=request.user)
    result['udfs'] = UDF.objects.all()
    disable = False
    if request.method == 'POST':
        form = PigScriptForm(request.POST)
        if not form.is_valid():
            raise PopupException(
                "".join(["%s: %s" % (field, error) for field, error in form.errors.iteritems()])
            )

        #Save or Create new script
        if request.POST.get('submit') == 'Save':
            if "autosave" in request.session:
                del request.session['autosave']
            if request.POST.get("script_id"):
                instance = PigScript.objects.get(pk=request.POST['script_id'])
                form = PigScriptForm(request.POST, instance=instance)
                form.save()
            else:
                instance = PigScript(**form.cleaned_data)
                instance.user = request.user
                instance.saved = True
                instance.save()
                if pig_script:
                    return redirect(index, obj_id=instance.pk)
                else:
                    obj_id = instance.pk

        #runing Explain
        if request.POST.get('submit') == 'Explain':
            script_path = '/pig_scripts/%s.pig' % '_'.join(request.POST['title'].replace('(', '').replace(')', '').split())
            pig_src = request.POST['pig_script']
            if 'register' in pig_src.lower():
                pig_src = reg_replace(pig_src)
            if request.POST.get("python_script"):
                pig_src = augmate_python_path(request.POST.get("python_script"), pig_src)
            pig = CommandPy("pig -e explain -script %s" % script_path, script_path, pig_src)
            result['stdout'] = pig.returnCode()
            #Sending 'script_id' to 'result' in order to avoid losing it
            if request.POST.get("script_id"):
                result.update({'id': request.POST['script_id']})
            result.update({'pig_script': request.POST['pig_script'], 'title': request.POST['title'], 'python_script': request.POST['python_script']})
            disable = True      #Turn of renew, because we have all data
            
    if not request.GET.get("new"):
        result.update(request.session.get("autosave", {}))
    
    # This is for 'View in pig' functions in Hcatalog and script cloning
    if pig_script and not disable:
        result.update({'pig_script': pig_script['pig_script'], 'title': pig_script['title'], 'python_script': pig_script['python_script']})
    
    #If we have obj_id, we renew or get instance to send it into form.
    if obj_id and not disable:
        instance = get_object_or_404(PigScript, pk=obj_id)
        for field in instance._meta.fields:
            result[field.name] = getattr(instance, field.name)
    return render('edit_script.mako', request, dict(result=result))

#Making normal path to our *.jar files
def reg_replace(pig_src):
    pig_split = pig_src.split('\n')
    a = lambda x: re.findall(r'.*(.\jar)$', x)
    pig_src_out = ''
    for item in pig_split:
        if 'register' in item.lower():
            filtered_a = filter(a, item.split())
            if filtered_a:
                item = item.replace(filtered_a[0], 'hdfs://ip-10-4-214-110.ec2.internal:8020/tmp/' + os.path.split(filtered_a[0])[1])
        pig_src_out += item + '\n'
    return pig_src_out

#Deleting PigScript objects
def delete(request, obj_id):
    instance = get_object_or_404(PigScript, pk=obj_id)
    instance.delete()
    return redirect(index)

#Clone script by obj_id to user forms
def script_clone(request, obj_id=None):
    pig_script = PigScript.objects.filter(user=request.user, id=obj_id).values()
    if pig_script:
        pig_script = pig_script[0]
    else:
        raise Http404
    del pig_script['id']
    del pig_script['date_created']
    return index(request, pig_script=pig_script)


def piggybank(request, obj_id = False):
    import posixpath

    from django.utils.translation import ugettext as _

    if request.method == 'POST':
        form = UDFForm(request.POST, request.FILES)

        if form.is_valid():
            uploaded_file = request.FILES['hdfs_file']
            dest = '/tmp'
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
                return redirect('pig_root', obj_id)
            else:
                return piggybank_index(request)

        else:
            raise PopupException(_("Error in upload form: %s") % (form.errors, ))

def piggybank_index(request, msg=None):
    udfs = UDF.objects.filter(owner=request.user)
    pig_script = PigScript.objects.filter(saved=True, user=request.user)
    udf_form = UDFForm(request.POST, request.FILES)
    return render('piggybank_index.mako', request, dict(udfs=udfs, pig_script=pig_script, udf_form = udf_form, msg = msg))


def udf_del(request, obj_id):
    udf = get_object_or_404(UDF, pk=obj_id)
    try:
        request.fs.remove(udf.url)
        msg = "<pre> Deleted %s from HDFS. </pre>" % udf.url
    except:
        msg = "<pre> Can't delete %s from HDFS, check if it exist. </pre>" % udf.url
    finally:
        msg = msg + '<pre> Deleted from database %s </pre>' % udf.file_name
        udf.delete()
    return piggybank_index(request, msg)


python_template = re.compile(r"(\w+)\.py")
def augmate_python_path(python_script, pig_script):
    with open('/tmp/python_udf.py', 'w') as f:
        f.write(python_script)
    return re.sub(python_template, '/tmp/python_udf.py', pig_script)


def start_job(request):
    if "autosave" in request.session:
        del request.session['autosave']
    t = Templeton(request.user.username)
    statusdir = "/tmp/.pigjobs/%s" % datetime.now().strftime("%s")
    script_file = statusdir + "/script.pig"
    pig_script = request.POST['pig_script']
    if request.POST.get("python_script"):
        pig_script = augmate_python_path(request.POST.get("python_script"), pig_script)
    pig_script = reg_replace(pig_script)
    _do_newfile_save(request.fs, script_file, pig_script, "utf-8")
    job = t.pig_query(pig_file=script_file, statusdir=statusdir, callback=request.build_absolute_uri("/pig/notify/$jobId/"))
    #job = t.pig_query(execute=request.POST['pig_script'], statusdir=statusdir)

    if request.POST.get("script_id"):
        script = PigScript.objects.get(pk=request.POST['script_id'])
    else:
        script = PigScript(user=request.user, saved=False, title=request.POST['title'])
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
        Job.objects.get(job_id=request.POST['job_id']).delete()
        return HttpResponse(json.dumps({"text": "Job %s was killed" % job_id}))
    except:
        return HttpResponse(json.dumps({"text": "An error was occured"}))


def _job_result(request, job):
    """

    """
    statusdir = job.statusdir
    result = {}
    try:
        error = request.fs.open(statusdir + "/stderr", "r")
        result['error'] = error.read()
        stdout = request.fs.open(statusdir + "/stdout", "r")
        result['stdout'] = stdout.read()
        exit_code = request.fs.open(statusdir + "/exit", "r")
        result['exit'] = exit_code.read()
        error.close()
        stdout.close()
        exit_code.close()
    except:
        raise Http404("Script data has been deleted.")
    return result


def get_job_result(request):
    job = Job.objects.get(job_id=request.POST['job_id'])
    result = {}
    try:
        result.update(_job_result(request, job))
    except:
        result['error'] = ""
        result['stdout'] = ""
        result['exit'] = ""
    return HttpResponse(json.dumps(result))


def query_history(request):
    return render("query_history.mako", request, dict(jobs=Job.objects.order_by("-script__date_created").all()))


def show_job_result(request, job_id):
    result = {}
    result['scripts'] = PigScript.objects.filter(saved=True, user=request.user)
    result['udfs'] = UDF.objects.all()
    job = Job.objects.get(job_id=job_id)
    if job.email_notification:
        result['email_notification'] = True
    if job.status == job.JOB_SUBMITED:
        result['job_id'] = job.job_id
        result['JOB_SUBMITED'] = True
    else:
        result.update(_job_result(request, job))
    result['stdout'] = result['stdout'].decode("utf-8")
    instance = job.script
    for field in instance._meta.fields:
        result[field.name] = getattr(instance, field.name)

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


@login_notrequired
def notify_job_complited(request, job_id):
    job = Job.objects.get(job_id=job_id)
    job.status = job.JOB_COMPLETED
    job.save()
    job_result = _job_result(request, job)
    if job.email_notification:
        subject = 'Query result'
        message = render_to_string(
            'mail/approved.html',
            {'user': job.script.user.username,
             'query': job.script.pig_script,
             'stdout': job_result['stdout'],
             "stderr": job_result['error']}
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        send_mail(subject, message, from_email, [job.script.user.email])
    return HttpResponse("Done")


def autosave_scripts(request):
    request.session['autosave'] = {
        "pig_script": request.POST['pig_script'],
        "python_script": request.POST.get('python_script'),
        "title": request.POST.get("title")
        }
    return HttpResponse(json.dumps("Done"))


def check_script_title(request):
    """
    Check script name for unique.
    """
    result = PigScript.objects.filter(title=request.GET.get("title")).count()
    return HttpResponse(json.dumps(not bool(result)))
