import settings

import json
import os

from django import forms

info = None


class RegistrationForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    phone = forms.CharField()
    email = forms.EmailField()
    company = forms.CharField()
    title = forms.CharField()
    country = forms.ChoiceField(choices=[(name, name) for name in ("USA", "Ukraine")])
    state = forms.CharField()
    industry = forms.ChoiceField(choices=[(name, name) for name in ("IT",)])
    company_size = forms.ChoiceField(choices=[(name, name) for name in ("Small", "Medium", "Large")])
    job_function = forms.ChoiceField(choices=[(name, name) for name in ("Manager", "Developer", "Sales")])
    send_usage = forms.BooleanField(initial=True, label="Send Anonymous Usage Statistics to Hortonworks")


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


def is_skipped():
    return os.path.exists(settings.USERINFO_FILE_PATH + ".skip")


load_info()
