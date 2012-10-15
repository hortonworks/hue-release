from djangomako.shortcuts import render_to_response
from django.shortcuts import redirect

from models import Section, Step

import settings
import os, time, string

def index(request):
    return render_to_response("lessons.html",{})

def lesson_list(request):
    sections = Section.objects.all()
    steps = map(lambda s : Step.objects.filter(section = s).order_by('order'),
                sections)
    now = int(time.time()) - 172800
    return render_to_response("lesson_list.html",{'lessons':sections,
                                                  'steps':steps,
                                                  'now':now,
												  'x':request.user,
												  })

def lesson(request, section_id, step):
    section = Section.objects.get(id = section_id)
    steps = Step.objects.filter(section = section).order_by('order')
    step = Step.objects.filter(section = section, order = step)[0]
    git_files = os.path.join(settings.PROJECT_PATH, 'run/git_files')
    filename = step.file_path

    html = string.join(file(os.path.join(git_files, filename)).readlines())
    return render_to_response("one_lesson.html", {'step' : step,
                                                  'max' : len(steps),
                                                  'step_html' : html})

def lesson_steps(request, section_id, step=0):
    section = Section.objects.get(id = section_id)
    steps = Step.objects.filter(section = section).order_by('order')
    return render_to_response("lesson.html", {'steps' : steps})

def content(request, page):
    if page == '':
        return redirect('/')
    return render_to_response("content.html", {})
