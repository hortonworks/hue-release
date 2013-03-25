# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'PigScript'
        db.create_table('pig_pigscript', (
            ('pig_script', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('saved', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('python_script', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('pig', ['PigScript'])

        # Adding model 'UDF'
        db.create_table('pig_udf', (
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('file_name', self.gf('django.db.models.fields.CharField')(max_length=55)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('pig', ['UDF'])

        # Adding model 'Job'
        db.create_table('pig_job', (
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
            ('email_notification', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('job_id', self.gf('django.db.models.fields.CharField')(max_length=50, primary_key=True)),
            ('script', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pig.PigScript'])),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('job_type', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
            ('statusdir', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('pig', ['Job'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'PigScript'
        db.delete_table('pig_pigscript')

        # Deleting model 'UDF'
        db.delete_table('pig_udf')

        # Deleting model 'Job'
        db.delete_table('pig_job')
    
    
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
            'job_type': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'script': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pig.PigScript']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'statusdir': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'pig.pigscript': {
            'Meta': {'object_name': 'PigScript'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pig_script': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'python_script': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'saved': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
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
