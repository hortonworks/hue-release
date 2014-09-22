# -*- coding: utf-8 -*-
from desktop.lib.rest import http_client
from desktop.conf import SERVER_USER
import simplejson as json
import urllib

from hcatalog.conf import TEMPLETON_URL, SECURITY_ENABLED


class Templeton(object):

    def __init__(self, user="hue"):
        self.user = SERVER_USER.get()
        self.doAs = user
        self.client = http_client.HttpClient(TEMPLETON_URL.get())
        if SECURITY_ENABLED.get():
            self.client = self.client.set_kerberos_auth()

    def get(self, url, data=None):
        """
        Make GET query to templeton url.
        """
        if data is not None:
            data['user.name'] = self.user
        else:
            data = {"user.name": self.user}

        data['doAs'] = self.doAs
        response = self.client.execute("GET", url, params=data)
        return json.loads(response.content)

    def post(self, url, data=None):
        """
        Make POST query to templeton url.
        """
        params = {"user.name": self.user, "doAs": self.doAs}
        data = urllib.urlencode([(k, v) for k, vs in data.iteritems()
                                 for v in isinstance(vs, list) and vs or [vs]])
        response = self.client.execute("POST", url, params=params, data=data)
        return json.loads(response.content)

    def put(self, url, data=None):
        """
        Make PUT query to templeton url.
        """
        try:
            params = {"user.name": self.user, "doAs": self.doAs}
            response = self.client.execute("PUT", url, params=params, data=data, headers={'Content-Type': 'application/json'})
            return json.loads(response.content)
        except http_client.RestException, error:
            try:
                return json.loads(error.content)
            except AttributeError:
                raise error

    def delete(self, url, params=None, data=None):
        """
        Make DELETE query to templeton url.
        """
        if params is not None:
            params["user.name"] = self.user
            params["doAs"] = self.doAs
        else:
            params = {"user.name": self.user, "doAs": self.doAs}
        response = self.client.execute("DELETE", url, params=params, data=data)
        return json.loads(response.content)

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
        return self.get("jobs/%s" % job_id)

    def kill_job(self, job_id):
        """
        Kill a job given its job ID.
        """
        return self.delete("jobs/%s" % job_id)
