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
import re
import logging
import simplejson as json
from datetime import datetime
import time

from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.utils.html import mark_safe
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.django_util import login_notrequired, render, get_desktop_uri_prefix
from desktop.conf import SERVER_USER
from filebrowser.views import _do_newfile_save, _file_reader, _upload_file
from jobbrowser.api import get_api
from jobbrowser import conf as jobbrowser_conf
from pig.models import PigScript, UDF, Job
from pig.templeton import Templeton
from pig.forms import PigScriptForm
from pig import conf

LOG = logging.getLogger(__name__)

UDF_PATH = conf.UDF_PATH.get()


def index(request, obj_id=None):
    result = {}
    result['scripts'] = PigScript.objects.filter(saved=True, user=request.user)
    result['udfs'] = UDF.objects.all()
    if request.method == 'POST':
        form = PigScriptForm(request.POST)
        if not form.is_valid():
            raise PopupException(
                "".join(["%s: %s" % (field, error) for field, error in form.errors.iteritems()])
            )
        form.cleaned_data["arguments"] = "\t".join(request.POST.getlist("pigParams"))
        if "autosave" in request.session:
            del request.session['autosave']
        if request.POST.get("script_id"):
            instance = PigScript.objects.get(pk=request.POST['script_id'])
            args = request.POST.copy()
            args["arguments"] = "\t".join(request.POST.getlist("pigParams"))
            form = PigScriptForm(args, instance=instance)
            form.save()
        else:
            instance = PigScript(**form.cleaned_data)
            instance.user = request.user
            instance.save()
        return redirect(reverse("view_script", args=[instance.pk]))
    if not request.GET.get("new"):
        result.update(request.session.get("autosave", {}))

    #If we have obj_id, we renew or get instance to send it into form.
    if obj_id:
        instance = get_object_or_404(PigScript, pk=obj_id)
        for field in instance._meta.fields:
            result[field.name] = getattr(instance, field.name)
    return render('edit_script.mako', request, dict(result=result))


#Making normal path to our *.jar files
udf_template = re.compile(r"register\s+(\S+\.jar)", re.I | re.M)
pythonudf_template = re.compile(r"register\s+[\'\"](\S+\.py)[\'\"]\s+using\s+jython\s+as\s+(\S+);", re.I | re.M)
parameters_template = re.compile(r"%(\w+)%")
macro_template = re.compile(r"import\s+[\"\'](/\S+\.(?:macro|pig))[\"\']\s*;?", re.I | re.M)


def process_pig_script(pig_src, request, statusdir):
    python_udf_path = request.fs.join(statusdir, "pythonudf.py")

    #1) Replace parameters with their values
    def get_param(matchobj):
        return request.POST.get("%" + matchobj.group(1) + "%")

    def get_file_path(matchobj):
        return "REGISTER " + request.fs.get_hdfs_path(request.fs.join(UDF_PATH, matchobj.group(1)))

    def get_macro_path(matchobj):
        return "IMPORT '" + request.fs.get_hdfs_path(matchobj.group(1)) + "';"

    def get_pythonudf_path(matchobj):
        return "REGISTER '%s' USING jython AS %s;" % (request.fs.get_hdfs_path(python_udf_path), matchobj.group(2))

    pig_src = re.sub(parameters_template, get_param, pig_src)
    pig_src = re.sub(udf_template, get_file_path, pig_src)
    pig_src = re.sub(macro_template, get_macro_path, pig_src)

    if pythonudf_template.match(pig_src) and request.POST.get("python_script"):
        _do_newfile_save(request.fs, python_udf_path, request.POST["python_script"], "utf-8")
        pig_src = re.sub(pythonudf_template, get_pythonudf_path, pig_src)
    return pig_src


#Deleting PigScript objects
def delete(request, obj_id):
    instance = get_object_or_404(PigScript, pk=obj_id)
    instance.delete()
    return redirect(index)


#Clone script by obj_id to user forms
def script_clone(request, obj_id):
    script = get_object_or_404(PigScript, pk=obj_id)
    request.session['autosave'] = {
        "arguments": script.arguments,
        "pig_script": script.pig_script,
        "python_script": script.python_script,
        "title": script.title + "(copy)"
    }
    return redirect(reverse("root_pig"))


def udf_get(request):
    udfs = UDF.objects.all()
    return HttpResponse(json.dumps(dict((u.id, u.file_name) for u in udfs)))


def udf_create(request):
    response = {'status': -1, 'data': ''}
    try:
        resp = _upload_file(request)
        response.update(resp)
        udf = UDF.objects.create(url=resp['path'], file_name=request.FILES['hdfs_file'].name, owner=request.user)
        response['udf_id'] = udf.id
    except Exception, ex:
        response['error'] = str(ex)
        hdfs_file = request.FILES.get('hdfs_file')
        if hdfs_file:
            hdfs_file.remove()
    return HttpResponse(json.dumps(response))


def udf_delete(request, obj_id=None):
    udf = get_object_or_404(UDF, pk=obj_id)
    status = -1
    message = ''
    try:
        request.fs.remove(udf.url)
        udf.delete()
        status = 0
        message = udf.file_name + " was successfully removed"
    except:
        message = "Can't delete %s from HDFS, check if it exist." % udf.url
    return HttpResponse(json.dumps({'status': status, 'message': message}))


def start_job(request):
    if "autosave" in request.session:
        del request.session['autosave']
    t = Templeton(request.user.username)
    statusdir = "/tmp/.pigjobs/%s/%s_%s" % (request.user.username, request.POST['title'].lower().replace(" ", "_"),  datetime.now().strftime("%s"))
    script_file = statusdir + "/script.pig"
    pig_script = request.POST['pig_script']
    pig_script = process_pig_script(pig_script, request, statusdir)
    _do_newfile_save(request.fs, script_file, pig_script, "utf-8")
    args = filter(bool, request.POST.getlist("pigParams"))
    job_type = Job.EXECUTE
    execute = None
    if request.POST.get("explain"):
        execute = "explain -script %s" % (request.fs.fs_defaultfs + script_file)
        job_type = Job.EXPLAINE
        script_file = None
    if request.POST.get("syntax_check"):
        args.append("-check")
        job_type = Job.SYNTAX_CHECK
    callback = request.build_absolute_uri("/pig/notify/$jobId/")
    LOG.debug("User %s started pig job via webhcat: curl -s -d file=%s -d statusdir=%s -d callback=%s %s" % (
        request.user.username, script_file, statusdir, callback, "".join(["-d arg=%s " % a for a in args])
    ))
    job = t.pig_query(pig_file=script_file, execute=execute, statusdir=statusdir, callback=callback, arg=args)

    if request.POST.get("script_id"):
        script = PigScript.objects.get(pk=request.POST['script_id'])
    else:
        script = PigScript(user=request.user, saved=False, title=request.POST['title'])
    script.pig_script = request.POST['pig_script']
    script.python_script = request.POST['python_script']
    script.arguments = "\t".join(args)
    script.save()
    Job.objects.create(user=script.user,
                       job_id=job['id'],
                       statusdir=statusdir,
                       script_title=script.title,
                       job_type=job_type,
                       email_notification=bool(request.POST.get('email')))
    return HttpResponse(
        json.dumps(
            {
                "job_id": job['id'],
                "text": "The Job <a href='%s' target='_blank'>%s</a> has been started successfully. <br>\
                You can always go back to <a href='%s'>Query History</a> for results after the run." % (
                    reverse("single_job", args=[job['id']]),
                    job['id'],
                    reverse("query_history")
                )
            }
        )
    )


def kill_job(request):
    t = Templeton(request.user.username)
    try:
        job_id = request.POST['job_id']
        t.kill_job(job_id)
        job = Job.objects.get(job_id=request.POST['job_id'])
        job.status = job.JOB_KILLED
        job.save()
        return HttpResponse(json.dumps({"text": "Job %s was killed" % job_id}))
    except:
        return HttpResponse(json.dumps({"text": "An error was occured"}))


def kill_job_by_jt(request):
    if request.method != "POST":
        raise Exception("kill_job may only be invoked with a POST (got a %(method)s).") % dict(method=request.method)
    job_id = request.POST['job_id']

    # check job permission
    try:
        api = get_api(request.user, request.jt)
        job = api.get_job(jobid=job_id)
    except Exception, e:
        return HttpResponse(json.dumps({"text": "Could not find job %s. The job might not be running yet." % job_id}))

    if not jobbrowser_conf.SHARE_JOBS.get() and not request.user.is_superuser and job.user != request.user.username:
        return HttpResponse(json.dumps({"text": "You don't have the permissions to access job %(id)s." % job_id}))
    if job.user != request.user.username and not request.user.is_superuser:
        return HttpResponse(
            json.dumps({"text": "Permission denied.  User %(username)s cannot delete user %(user)s's job." %
                                dict(username=request.user.username, user=job.user)}))
    # killing job
    job.kill()
    cur_time = time.time()
    while time.time() - cur_time < 15:
        if job.status not in ["RUNNING", "QUEUED"]:
            # updating job status in pig query history
            job = Job.objects.get(job_id=job_id)
            job.status = job.JOB_KILLED
            job.save()
            return HttpResponse(json.dumps({"text": "Job %s was killed" % job_id}))
        time.sleep(1)
        job = api.get_job(jobid=job_id)
    return HttpResponse(json.dumps({"text": "An error was occurred: job did not appear as killed within 15 seconds"}))


def _job_result(request, job):
    statusdir = job.statusdir
    result = {}
    try:
        stderr_file = statusdir + "/stderr"
        stdout_file = statusdir + "/stdout"
        exit_code_file = statusdir + "/exit"
        pig_script_file = statusdir + "/script.pig"
        python_udf_file = statusdir + "/pythonudf.py"
        error = request.fs.read(stderr_file, 0, request.fs.stats(stderr_file).size)
        stdout = request.fs.read(stdout_file, 0, request.fs.stats(stdout_file).size)
        exit_code = request.fs.read(exit_code_file, 0, request.fs.stats(exit_code_file).size)
        pig_script = request.fs.read(pig_script_file, 0, request.fs.stats(pig_script_file).size)
        try:
            result['python_script'] = mark_safe(request.fs.read(python_udf_file, 0, request.fs.stats(python_udf_file).size))
        except:
            pass
        result['error'] = mark_safe(error)
        result['stdout'] = mark_safe(stdout)
        result['exit'] = mark_safe(exit_code)
        result['pig_script'] = mark_safe(pig_script)
        if job.job_type == job.SYNTAX_CHECK:
            result['stdout'] = result['error']
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


def get_job_result_stderr(request):
    job = Job.objects.get(job_id=request.POST['job_id'])
    statusdir = job.statusdir
    result = {}
    try:
        stderr_file = statusdir + "/stderr"
        error = request.fs.read(stderr_file, 0, request.fs.stats(stderr_file).size)
        result['stderr'] = mark_safe(error)
    except:
        result['stderr'] = ""
    return HttpResponse(json.dumps(result))


def get_job_result_stdout(request):
    job = Job.objects.get(job_id=request.POST['job_id'])
    statusdir = job.statusdir
    result = {}
    try:
        stderr_file = statusdir + "/stderr"
        stdout_file = statusdir + "/stdout"
        stdout = request.fs.read(stdout_file, 0, request.fs.stats(stdout_file).size)
        result['stdout'] = mark_safe(stdout)
        if job.job_type == job.SYNTAX_CHECK:
            error = request.fs.read(stderr_file, 0, request.fs.stats(stderr_file).size)
            result['stdout'] = mark_safe(error)
    except:
        result['stdout'] = ""
    return HttpResponse(json.dumps(result))


def get_job_result_script(request):
    job = Job.objects.get(job_id=request.POST['job_id'])
    statusdir = job.statusdir
    result = {}
    try:
        pig_script_file = statusdir + "/script.pig"
        pig_script = request.fs.read(pig_script_file, 0, request.fs.stats(pig_script_file).size)
        result['pig_script'] = mark_safe(pig_script)
    except:
        result['pig_script'] = ""
    return HttpResponse(json.dumps(result))


def query_history(request):
    jobs_list = Job.objects.filter(user=request.user).order_by("-start_time").all()
    paginator = Paginator(jobs_list, 20)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        jobs = paginator.page(page)
    except (EmptyPage, InvalidPage):
        jobs = paginator.page(paginator.num_pages)

    return render(
        "query_history.mako",
        request,
        {"jobs": jobs}
    )


def query_history_job_detail(request, job_id):
    jobs_list = [get_object_or_404(Job, user=request.user, job_id=job_id)]
    paginator = Paginator(jobs_list, 20)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        jobs = paginator.page(page)
    except (EmptyPage, InvalidPage):
        jobs = paginator.page(paginator.num_pages)

    return render(
        "query_history.mako",
        request,
        {"jobs": jobs}
    )


def show_job_result(request, job_id):
    result = {}
    result['scripts'] = PigScript.objects.filter(saved=True, user=request.user)
    result['udfs'] = UDF.objects.all()
    job = Job.objects.get(job_id=job_id)
    result['job_id'] = job.job_id
    if job.email_notification:
        result['email_notification'] = True
    instance = job.script
    for field in instance._meta.fields:
        result[field.name] = getattr(instance, field.name)
    if job.status == job.JOB_SUBMITTED:
        result['JOB_SUBMITTED'] = True
    else:
        result.update(_job_result(request, job))
        result['stdout'] = result['stdout'].decode("utf-8")
    return render('edit_script.mako', request, dict(result=result))


def delete_job_object(request):
    try:
        job = Job.objects.get(job_id=request.POST['job_id'])
    except:
        return HttpResponse(json.dumps({"status": -1}))
    else:
        request.fs.rmtree(job.statusdir)
        job.delete()
    return HttpResponse(json.dumps({"status": 0}))


def check_running_job(request, job_id):
    t = Templeton(request.user.username)
    job = Job.objects.get(job_id=job_id)
    if job is not None:
        try:
            result = t.check_job(job_id)
            exitValue = result['exitValue'] if 'exitValue' in result else None
            completed = result['completed'] if 'completed' in result else None
            runState = result['status']['runState'] if 'status' in result and 'runState' in result['status'] else None
            if runState == job.TEMPLETON_JOB_RUN_STATE_KILLED:
                job.status = job.JOB_KILLED
            elif runState == job.TEMPLETON_JOB_RUN_STATE_FAILED or \
                    (completed and exitValue is not None and exitValue != 0):
                job.status = job.JOB_FAILED
            job.save()
            return HttpResponse(json.dumps({"status": job.status}))
        except Exception, ex:
            LOG.debug(unicode(ex))
    return HttpResponse(json.dumps({"status": 0}))


@login_notrequired
def notify_job_completed(request, job_id):
    t = Templeton(SERVER_USER.get())
    job = Job.objects.get(job_id=job_id)
    job.status = job.JOB_COMPLETED
    try:
        result = t.check_job(job_id)
        exitValue = result['exitValue'] if 'exitValue' in result else None
        completed = result['completed'] if 'completed' in result else None
        runState = result['status']['runState'] if 'status' in result and 'runState' in result['status'] else None
        if runState == job.TEMPLETON_JOB_RUN_STATE_KILLED:
            job.status = job.JOB_KILLED
        elif runState == job.TEMPLETON_JOB_RUN_STATE_FAILED or (completed and exitValue is not None and exitValue != 0):
            job.status = job.JOB_FAILED
    except Exception, ex:
        LOG.debug(unicode(ex))
    job.save()
    if job.email_notification:
        subject = 'Query result'
        body = "Your PIG script '%s' started at %s has been completed.\n\
        You can check result at the following link %s" % (
            job.script.title,
            job.start_time.strftime('%d.%m.%Y %H:%M'),
            "%s%s" % (get_desktop_uri_prefix(), reverse("query_history_job_detail", args=[job_id]))
        )
        job.script.user.email_user(subject, body)
    return HttpResponse("Done")


def autosave_scripts(request):
    request.session['autosave'] = {
        "pig_script": request.POST['pig_script'],
        "python_script": request.POST.get('python_script'),
        "title": request.POST.get("title"),
        "arguments": "\t".join(request.POST.getlist("pigParams"))
    }
    return HttpResponse(json.dumps("Done"))


def check_script_title(request):
    """
    Check script name for unique.
    """
    result = PigScript.objects.filter(title=request.GET.get("title"), saved=True, user=request.user).count()
    return HttpResponse(json.dumps(not bool(result)))


def download_job_result(request, job_id):
    job = get_object_or_404(Job, job_id=job_id)
    if job.status != job.JOB_COMPLETED:
        raise PopupException("Job not completed yet")
    path = job.statusdir + "/stdout"
    stdout = request.fs.open(path, "r")
    stats = request.fs.stats(path)
    response = HttpResponse(_file_reader(stdout), content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="%s_result.txt"' % job_id
    response["Content-Length"] = stats['size']
    return response


def ping_job(request, job_id):
    t = Templeton(request.user.username)
    try:
        result = t.check_job(job_id)
    except Exception, ex:
        result = {"status": {"failureInfo": unicode(ex)}}
    return HttpResponse(json.dumps(result))