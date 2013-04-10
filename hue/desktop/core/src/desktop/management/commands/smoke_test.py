# -*- coding: utf-8 -*-
import sys
from django.core.management.base import NoArgsCommand
from hadoop import cluster
from filebrowser.views import _do_newfile_save
from desktop.views import _get_config_errors


class Command(NoArgsCommand):
    """Running smoke integration tests."""
    def handle_noargs(self, **options):
        error_list = _get_config_errors()
        error_message = ""
        for confvar, error in error_list:
            if isinstance(confvar, str):
                cv = confvar
            else:
                cv = confvar.get_fully_qualifying_key()
            error_message += "\n--Variable: %s\n--Current value: %s\n--Error: %s\n" % (cv, confvar.get(), error)

        if error_message:
            sys.stderr.write("Possible missconfigurations: \n %s \n" % error_message)
        #self.test_filebrowser()
        #self.test_beeswax()
        #self.test_pig()
        #self.test_jobDesigner()
        #self.test_oozie()

    def test_filebrowser(self):
        sys.stdout.write("Checking HDFS access\n")
        fs = cluster.get_hdfs()
        try:
            _do_newfile_save(fs, "/tmp/smoke_fb.test", "Test", "utf-8")
            fs.remove("/tmp/smoke_fb.test")
        except Exception, ex:
            sys.stderr.write("[Hdfs/WebHdfs] Exception: %s \n" % ex)

    def test_beeswax(self):
        sys.stdout.write("Checking Hive/Beeswax/Hcatalog configuration\n")

    def test_pig(self):
        sys.stdout.write("Checking Pig config\n")

    def test_jobDesigner(self):
        sys.stdout.write("Checking JobDesighner config\n")

    def test_oozie(self):
        sys.stdout.write("Checking Oozie config\n")
