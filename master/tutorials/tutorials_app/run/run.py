import sys, os
from time import time
import string

dirs = os.path.abspath(os.curdir).split(os.path.sep)
app = string.join(dirs[:-2],os.path.sep)
sys.path.append(app)
os.environ['DJANGO_SETTINGS_MODULE'] = "tutorials_app.settings"

from tutorials_app.models import Section, Step

def listfolders(folder):
    return [f for f in os.listdir(folder)
              if os.path.isdir(os.path.join(folder,f)) and f[0]!='.']

current_dir = os.path.join(os.path.abspath(os.curdir), 'git_files')
sections = listfolders(current_dir)

all_sections = list(Section.objects.all())

for section_name in sections:
    section_dir = os.path.join(current_dir, section_name)
    section_name = section_name.replace('_', ' ').capitalize()
    
    try:
        del all_sections[map(lambda x:x.name, all_sections).\
                     index(section_name)]
    except ValueError:
        pass

    try:
        section = Section.objects.get(name = section_name)
    except Section.DoesNotExist:
        section = Section(name = section_name, order = 100,
                          description = '', section_level = 1,
                          section_user_type = 1, lesson_name = '',
                          add_time = int(time()))
        section.save()
    
    all_steps = list(Step.objects.filter(section=section))

    orders = listfolders(section_dir)
    for order in orders:
        order_dir = os.path.join(section_dir, order)
        files = os.listdir(order_dir)
        for f in filter(lambda x:x.endswith(".html"), files):
            fl = os.path.join(order_dir, f)
            step_name = f[:f.rfind('.')]
            step_name = step_name.replace('_', ' ').capitalize()
    
            try:
                del all_steps[map(lambda x:x.name, all_steps).\
                        index(step_name)]
            except ValueError:
                pass

            print step_name, order, section_name

            try:
                step = Step.objects.get(order = order,
                                       section = section)
                step.name = step_name
                step.file_path = fl
                step.save()
            except Step.DoesNotExist:
                step = Step(name = step_name, order = order,
                            file_path = fl, add_time = int(time()),
                            section = section)
                step.save()
    map(lambda x:x.delete(), all_steps)

map(lambda x:x.delete(), all_sections)
