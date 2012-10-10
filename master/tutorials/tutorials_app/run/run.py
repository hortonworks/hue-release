import sys, os
from time import time
import string

dirs = os.path.abspath(os.curdir).split(os.path.sep)
app = string.join(dirs[:-2],os.path.sep)
sys.path.append(app)
os.environ['DJANGO_SETTINGS_MODULE'] = "tutorials_app.settings"

#import settings
from tutorials_app.models import Section, Step

current_dir = os.path.join(os.path.abspath(os.curdir), 'git_files')
files = os.listdir(current_dir)
for fl in files:
    file_name = fl[:-5]
    print file_name
    if fl[-5:] == '.html':
        file_name_parse = file_name.split('_')
        order = None
        for fp in file_name_parse:
            try:
                order = int(fp)
                break
            except:
                pass
        if order:
            section_name, step_name = file_name.split('_%d_' % order)
            section_name = section_name.replace('_', ' ').capitalize()
            step_name = step_name.replace('_', ' ').capitalize()
            try:
                section = Section.objects.get(name = section_name)
            except Section.DoesNotExist:
                section = Section(name = section_name, order = 100,
                                  description = '', section_level = 1,
                                  section_user_type = 1, lesson_name = '',
                                  add_time = int(time()))
                section.save()

            try:
                step = Step.objects.get(name = step_name,
                                       section = section)
                step.order = order
                step.file_path = fl
                step.save()
            except Step.DoesNotExist:
                step = Step(name = step_name, order = order,
                            file_path = fl, add_time = int(time()),
                            section = section)
                step.save()
