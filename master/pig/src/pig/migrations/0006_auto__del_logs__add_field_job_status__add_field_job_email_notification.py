# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting model 'Logs'
        db.delete_table('pig_logs')

        # Adding field 'Job.status'
        db.add_column('pig_job', 'status', self.gf('django.db.models.fields.SmallIntegerField')(default=2), keep_default=False)

        # Adding field 'Job.email_notification'
        db.add_column('pig_job', 'email_notification', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True), keep_default=False)

        # Deleting field 'PigScript.text'
        db.delete_column('pig_pigscript', 'text')

        # Deleting field 'PigScript.creater'
        db.delete_column('pig_pigscript', 'creater_id')

        # Adding field 'PigScript.pig_script'
        db.add_column('pig_pigscript', 'pig_script', self.gf('django.db.models.fields.TextField')(default=' '), keep_default=False)

        # Adding field 'PigScript.user'
        db.add_column('pig_pigscript', 'user', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['auth.User']), keep_default=False)

        # Adding field 'PigScript.saved'
        db.add_column('pig_pigscript', 'saved', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Adding field 'PigScript.python_script'
        db.add_column('pig_pigscript', 'python_script', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Changing field 'PigScript.date_created'
        db.alter_column('pig_pigscript', 'date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))
    
    
    def backwards(self, orm):
        
        # Adding model 'Logs'
        db.create_table('pig_logs', (
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('script_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('pig', ['Logs'])

        # Deleting field 'Job.status'
        db.delete_column('pig_job', 'status')

        # Deleting field 'Job.email_notification'
        db.delete_column('pig_job', 'email_notification')

        # Adding field 'PigScript.text'
        db.add_column('pig_pigscript', 'text', self.gf('django.db.models.fields.TextField')(default=' ', blank=True), keep_default=False)

        # Adding field 'PigScript.creater'
        db.add_column('pig_pigscript', 'creater', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['auth.User']), keep_default=False)

        # Deleting field 'PigScript.pig_script'
        db.delete_column('pig_pigscript', 'pig_script')

        # Deleting field 'PigScript.user'
        db.delete_column('pig_pigscript', 'user_id')

        # Deleting field 'PigScript.saved'
        db.delete_column('pig_pigscript', 'saved')

        # Deleting field 'PigScript.python_script'
        db.delete_column('pig_pigscript', 'python_script')

        # Changing field 'PigScript.date_created'
        db.alter_column('pig_pigscript', 'date_created', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True))
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'pig.job': {
            'Meta': {'object_name': 'Job'},
            'email_notification': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'job_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'}),
            'script': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pig.PigScript']"}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '2'}),
            'statusdir': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'pig.pigscript': {
            'Meta': {'object_name': 'PigScript'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pig_script': ('django.db.models.fields.TextField', [], {}),
            'python_script': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'saved': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'pig.udf': {
            'Meta': {'object_name': 'UDF'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'file_name': ('django.db.models.fields.CharField', [], {'max_length': '55'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }
    
    complete_apps = ['pig']
