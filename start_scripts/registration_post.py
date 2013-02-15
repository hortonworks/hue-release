import os

USERINFO_FILE_PATH = os.path.join(os.path.expanduser('~sandbox'),
                        'user_info.dat')
MARKETO_URL = "http://app-l.marketo.com/index.php/leadCapture/save"
CRON_FILE = "/etc/cron.d/1sandbox_registration"
CRON_FILE_ORIGIN = "/home/sandbox/start_scripts/registration_post_cron"

LOG = file("/var/log/registration_post.log", "a+")

if os.path.exists(USERINFO_FILE_PATH):
    #DO post
    import urllib2

    data = file(USERINFO_FILE_PATH).read()

    request = urllib2.Request(MARKETO_URL)
    request.data = data
    try:
        urllib2.urlopen(request)
    except:
        print >>LOG, "Failed to upload."
    else:
        os.rename(USERINFO_FILE_PATH, USERINFO_FILE_PATH + ".posted")
        print >>LOG, "Uploaded successful."

elif not os.path.exists(USERINFO_FILE_PATH + ".posted"):
    #Not registered yet. Add script to cron
    if not os.path.exists(CRON_FILE):
        with file(CRON_FILE, "w") as f:
            f.write(file(CRON_FILE_ORIGIN).read())
        print >>LOG, "Script added to cron"

else:
    #Registered. Remove cron task
    os.remove(CRON_FILE)
    print >>LOG, "Script removed from crontab"
