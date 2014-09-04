# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'ExportState'
        db.create_table('db2_export_exportstate', (
            ('last_state', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('finished_rows', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('update_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('finished_size', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('query_history', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['beeswax.QueryHistory'])),
            ('create_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('table', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('schema', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('comitted_rows', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('size', self.gf('django.db.models.fields.IntegerField')(default=-1)),
        ))
        db.send_create_signal('db2_export', ['ExportState'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'ExportState'
        db.delete_table('db2_export_exportstate')
    
    
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
        'beeswax.queryhistory': {
            'Meta': {'object_name': 'QueryHistory'},
            'design': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['beeswax.SavedQuery']", 'null': 'True'}),
            'has_results': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_state': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'log_context': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True'}),
            'modified_row_count': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'notify': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'operation_type': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'query': ('django.db.models.fields.TextField', [], {}),
            'query_stats': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'query_type': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'result_rows': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'result_size': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'server_guid': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '1024', 'null': 'True'}),
            'server_host': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'}),
            'server_id': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True'}),
            'server_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'}),
            'server_port': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'server_type': ('django.db.models.fields.CharField', [], {'default': "'beeswax'", 'max_length': '128'}),
            'statement_number': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'submission_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'beeswax.beeswaxqueryhistory': {
            'Meta': {'object_name': 'BeeswaxQueryHistory', 'db_table': "'beeswax_queryhistory'", '_ormbases': ['beeswax.QueryHistory']}
        },
        'beeswax.savedquery': {
            'Meta': {'object_name': 'SavedQuery'},
            'data': ('django.db.models.fields.TextField', [], {'max_length': '65536'}),
            'desc': ('django.db.models.fields.TextField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_auto': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'is_trashed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'db2_export.exportstate': {
            'Meta': {'object_name': 'ExportState'},
            'comitted_rows': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'create_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'finished_rows': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'finished_size': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_state': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'query_history': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['beeswax.QueryHistory']"}),
            'schema': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'size': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'table': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'update_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'})
        }
    }
    
    complete_apps = ['db2_export']
