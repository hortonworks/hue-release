import settings

import json
import os

from django import forms

info = None

class RegistrationForm(forms.Form):
    name = forms.CharField()
    lastname = forms.CharField()
    email = forms.EmailField()

def load_info():
    global info
    if os.path.exists(settings.USERINFO_FILE_PATH):
        info = json.load(file(settings.USERINFO_FILE_PATH))
    else:
        info = None
    return info

def save(dct):
    with file(settings.USERINFO_FILE_PATH, "w") as f:
        f.write(json.dumps(dct))

    newfile_flag = settings.USERINFO_FILE_PATH + ".newfile"
    with file(newfile_flag, 'a'):
        os.utime(newfile_flag, None)

load_info()