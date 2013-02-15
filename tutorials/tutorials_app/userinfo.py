import settings

import os


info = False


def load_info():
    global info
    if os.path.exists(settings.USERINFO_FILE_PATH) or \
       os.path.exists(settings.USERINFO_FILE_PATH + ".posted"):
        info = True
    else:
        info = False
    return info


def save(request):
    with file(settings.USERINFO_FILE_PATH, "w") as f:
        f.write(request)


def is_skipped():
    return os.path.exists(settings.USERINFO_FILE_PATH + ".skip")


load_info()
