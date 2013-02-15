import os
import pwd, grp
from datetime import datetime

USERINFO_FILE_PATH = os.path.join(os.path.expanduser('~sandbox'),
                        'user_info.dat')
MARKETO_URL = "http://app-l.marketo.com/index.php/leadCapture/save"
CRON_FILE = "/etc/cron.d/1sandbox_registration"
CRON_FILE_ORIGIN = "/home/sandbox/start_scripts/registration_post_cron"

LOG_FILE = "/home/sandbox/tutorials/registration_post.log"


def do_post():
    with file(LOG_FILE, "a+") as LOG:

        def log(s):
            print >>LOG, "[%s] %s" % (datetime.now().strftime("%d_%m_%Y_%H-%M-%S"), s)
            LOG.flush()

        if os.path.exists(USERINFO_FILE_PATH):
            #DO post
            log("Try to upload...")
            import urllib2

            data = file(USERINFO_FILE_PATH).read()

            request = urllib2.Request(MARKETO_URL)
            request.data = data
            try:
                urllib2.urlopen(request)
            except:
                log("Failed to upload.")
            else:
                os.rename(USERINFO_FILE_PATH, USERINFO_FILE_PATH + ".posted")
                log("Uploaded successful.")

        elif not os.path.exists(USERINFO_FILE_PATH + ".posted"):
            #Not registered yet. Add script to cron
            if not os.path.exists(CRON_FILE):
                with file(CRON_FILE, "w") as f:
                    f.write(file(CRON_FILE_ORIGIN).read())
                log("Script added to cron")

        else:
            #Registered. Remove cron task
            os.remove(CRON_FILE)
            log("Script removed from crontab")

if __name__ == '__main__':
    do_post()
    uid = pwd.getpwnam('sandbox').pw_uid
    gid = pwd.getgrnam('sandbox').gr_gid
    os.chown(LOG_FILE, uid, gid)
