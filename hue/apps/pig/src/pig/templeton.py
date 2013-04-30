# -*- coding: utf-8 -*-
import urllib
import urllib2
import simplejson as json
from hcatalog.conf import TEMPLETON_URL


class Templeton(object):

    def __init__(self, user="hdfs"):
        self.user = user

    def get(self, url, data=None):
        """
        Make GET query to templeton url.
        """
        if data is not None:
            data['user.name'] = self.user
        else:
            data = {"user.name": self.user}
        data = urllib.urlencode(data)
        response = urllib2.urlopen(TEMPLETON_URL.get() + url + "?" + data)
        return json.loads(response.read())

    def post(self, url, data=None):
        """
        Make POST query to templeton url.
        """
        if data is not None:
            data['user.name'] = self.user
        else:
            data = {"user.name": self.user}
        data = urllib.urlencode(data)
        req = urllib2.Request(TEMPLETON_URL.get() + url, data)
        response = urllib2.urlopen(req)

        return json.loads(response.read())

    def put(self, url, data=None):
        """
        Make PUT query to templeton url.
        """
        req = urllib2.Request(TEMPLETON_URL.get() + url + "?user.name=" + self.user, data, {'Content-Type': 'application/json'})
        req.get_method = lambda: 'PUT'
        try:
            response = urllib2.urlopen(req)
            return json.loads(response.read())
        except urllib2.HTTPError, error:
            return json.loads(error.read())

    def delete(self, url, data=None):
        """
        Make DELETE query to templeton url.
        """
        if data is not None:
            data['user.name'] = self.user
        else:
            data = {"user.name": self.user}
        data = urllib.urlencode(data)
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        req = urllib2.Request(TEMPLETON_URL.get() + url + "?" + data)
        req.get_method = lambda: 'DELETE'
        response = opener.open(req)
        return json.loads(response.read())

    def pig_query(self, execute=None, pig_file=None, statusdir=None, callback=None, arg=None):
        """
        Create and queue a Pig job.

        Keyword arguments:
        user -- Hue/Hadoop user
        execute -- String containing an entire, short pig program to run. (e.g. pwd)
        file -- HDFS file name of a pig program to run. (One of either "execcute" or "file" is required )
        statusdir -- A directory where Templeton will write the status of the Pig job. If
                     provided, it is the caller's responsibility to remove this directory when done.
        callback -- Define a URL to Optional be called upon job completion. You may embed a specific job
                    ID into this URL using $jobId. This tag will be replaced in the callback URL with this job's job
                    ID.
        arg -- Set a program argument. Optional None
        Returns dict:
        id -- A string containing the job ID similar to "job_201110132141_0001".
        info -- A JSON object containing the information returned when the job was queued.
        """
        if not any([execute, pig_file]):
            raise Exception("""One of either "execcute" or "file" is required""")
        data = {}
        if execute:
            data['execute'] = execute
        if pig_file:
            data['file'] = pig_file
        if statusdir:
            data['statusdir'] = statusdir
        if callback:
            data['callback'] = callback
        if arg:
            data['arg'] = arg
        return self.post("pig", data)

    def hive_query(self, execute=None, hive_file=None, statusdir=None, callback=None, arg=None):
        """
        Create and queue a Hive job.

        Keyword arguments:
        user -- Hue/Hadoop user
        execute -- String containing an entire, short hive program to run. (e.g. pwd)
        file -- HDFS file name of a hive program to run. (One of either "execcute" or "file" is required )
        statusdir -- A directory where Templeton will write the status of the Hive job. If
                     provided, it is the caller's responsibility to remove this directory when done.
        callback -- Define a URL to Optional be called upon job completion. You may embed a specific job
                    ID into this URL using $jobId. This tag will be replaced in the callback URL with this job's job
                    ID.
        arg -- Set a program argument. Optional None
        Returns dict:
        id -- A string containing the job ID similar to "job_201110132141_0001".
        info -- A JSON object containing the information returned when the job was queued.
        """
        if not any([execute, hive_file]):
            raise Exception("""One of either "execcute" or "file" is required""")
        data = {}
        if execute:
            data['execute'] = execute
        if hive_file:
            data['file'] = hive_file
        if statusdir:
            data['statusdir'] = statusdir
        if callback:
            data['callback'] = callback
        if arg:
            data['arg'] = arg
        return self.post("hive", data)

    def check_job(self, job_id):
        """
        Check the status of a job and get related job information given its job ID.
        """
        return self.get("queue/%s" % job_id)

    def kill_job(self, job_id):
        """
        Kill a job given its job ID.
        """
        return self.delete("queue/%s" % job_id)
