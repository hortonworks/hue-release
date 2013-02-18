import settings

import os
import sys

from multiprocessing import Process

info = False


def load_info():
    global info
    if os.path.exists(settings.USERINFO_FILE_PATH) or \
       os.path.exists(settings.USERINFO_FILE_PATH + ".posted"):
        info = True
    else:
        info = False
    return info


def is_skipped():
    # return os.path.exists(settings.USERINFO_FILE_PATH + ".skip")
    return False


def save(request):
    if is_skipped():
        os.remove(settings.USERINFO_FILE_PATH + ".skip")

    with file(settings.USERINFO_FILE_PATH, "w") as f:
        f.write(request)

    def upload():
        sys.path.append(settings.START_SCRIPTS)
        import registration_post
        registration_post.do_post()

    Process(target=upload).start()
    # upload()


load_info()
