import sys
import os
import string
from time import time
import subprocess

dirs = os.path.abspath(os.curdir).split(os.path.sep)
app = string.join(dirs[:-2],os.path.sep)
sys.path.append(app)
os.environ['DJANGO_SETTINGS_MODULE'] = "tutorials_app.settings"

from tutorials_app.models import Section, Step, VERSION

def listfolders(folder):
    return [f for f in os.listdir(folder)
              if os.path.isdir(os.path.join(folder,f)) and f[0]!='.']

current_dir = os.path.join(os.path.abspath(os.curdir), 'git_files')

# Check DB version. If new then do syncdb again.
new_version = False
VERSION_FILE = os.path.abspath(os.path.join(os.path.abspath(os.curdir), '../db/db_version.txt'))
if not os.path.exists(VERSION_FILE):
    new_version = True
else:
    try:
        old_version = int(file(VERSION_FILE).read())
        new_version = VERSION > old_version
    except ValueError:
        new_version = True

if new_version:
    RUN = os.path.abspath(os.path.join(os.path.abspath(os.curdir), 'run.sh'))
    subprocess.call(['bash', RUN, "--migrate"], shell=True)
    print>>file(VERSION_FILE, 'w'), VERSION

all_sections = list(Section.objects.all())

for tutorial_name in listfolders(current_dir):
    tutorial_dir = os.path.join(current_dir, tutorial_name)

    for lesson in listfolders(tutorial_dir):
        lesson_dir = os.path.join(tutorial_dir, lesson)
        lesson_name = lesson.split()
        lesson_order = int(lesson_name[1])
        description_file = os.path.join(lesson_dir, 'description.txt')
        if os.path.exists(description_file):
            description = open(description_file, 'r').read()
        else:
            description = ''

        lesson_title = '-'.join(lesson.split('-')[1:]).strip()

        try:
            section = Section.objects.get(order=lesson_order,
                                          lesson_name = tutorial_name)
            section.description = description
            section.lesson_title = lesson_title
            section.save()
            del all_sections[[s.id for s in all_sections].\
                             index(section.id)]
        except Section.DoesNotExist:
            section = Section(order = lesson_order,
                              lesson_name = tutorial_name,
                              add_time = int(time()),
                              description = description,
                              lesson_title = lesson_title)
            section.save()

        all_steps = list(Step.objects.filter(section=section))
        for step in os.listdir(lesson_dir):
            if step.endswith(".html"):
                step_name = step[:-5].split()
                step_order = int(step_name[-1])

                step_path = os.path.join(tutorial_name, lesson, step)

                try:
                    step_obj = Step.objects.get(order = step_order,
                                                section = section)
                    del all_steps[[s.id for s in all_steps].\
                                  index(step_obj.id)]
                    step_obj.file_path = step_path
                    step_obj.save()
                except Step.DoesNotExist:
                    step_obj = Step(order = step_order, file_path = step_path,
                                    add_time = int(time()), section = section)
                    step_obj.save()

            print '%s -> %s' % (lesson, step)
        [s.delete() for s in all_steps]
[s.delete() for s in all_sections]
