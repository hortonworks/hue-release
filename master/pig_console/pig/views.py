import os
try:
    import json
except ImportError:
    import simplejson as json

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from datetime import date

from django.test.client import Client
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django import forms

from pig.models import PigScript
from profile.models import Profile


class PigScriptForm(forms.Form):
    title = forms.CharField(max_length=100, required=False)
    text = forms.CharField(widget=forms.Textarea, required=False)
    is_temporery = forms.BooleanField(required=False)


@login_required
def index(request):
    profile = Profile.objects.get(user=request.user)
    pig_script = PigScript.objects.filter(creater=profile)
    paginator = Paginator(pig_script, 10)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        contacts = paginator.page(page)
    except (EmptyPage, InvalidPage):
        contacts = paginator.page(paginator.num_pages)
    page_count = range(1, paginator.num_pages + 1)

    form = PigScriptForm()
    if request.method == 'POST':
        form = PigScriptForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data['creater'] = profile
            name = '{u}_{n}.pig'.format(u=request.user.username,
                                        n=data['title'])
            folder = '{t}'.format(t=date.today().isoformat())
            script_folder = 'media/pig_script'
            if folder not in os.listdir(script_folder):
                os.makedirs(os.path.join(script_folder, folder))

            file_name = os.path.join(script_folder, folder, name)
            ffile = StringIO()
            ffile.write(data['text'])
            data['pig_script'] = SimpleUploadedFile(
                file_name, ffile.getvalue(), content_type='application/x-mplayer2')
            ps = PigScript.objects.create(**data)
            return redirect(one_script, ps.id)

    return render_to_response('index.html', RequestContext(request, {
        'form': form, 'contacts': contacts, 'page_count': page_count}))


@login_required
def one_script(request, obj_id):
    instance = PigScript.objects.filter(id=obj_id)
    if request.method == 'POST':
        form = PigScriptForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            file_name = instance[0].pig_script.path
            ffile = open(file_name, 'w+')
            ffile.write(data['text'])
            ffile.close()
            PigScript.objects.filter(id=obj_id).update(**data)

    form = PigScriptForm(instance.values('title', 'text', 'is_temporery')[0])
    return render_to_response('edit_script.html', RequestContext(
        request, {'form': form, 'instance': instance[0]}))


def execute(request, obj_id):
    #instance = PigScript.objects.get(id=obj_id)
    c = Client()
    #data = json.dumps({"script": instance.text})
    q = c.get('/api/v1/jobs/?format=json', content_type='application/json')
    return HttpResponse('<a href="{% url root_pig %}">back</a>' + q.content)
