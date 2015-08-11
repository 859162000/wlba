# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Lottery'
        db.create_table(u'wanglibao_lottery_lottery', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='lottery', to=orm['auth.User'])),
            ('buy_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('lottery_type', self.gf('django.db.models.fields.CharField')(default='\xe5\x8f\x8c\xe8\x89\xb2\xe7\x90\x83', max_length=50)),
            ('money_type', self.gf('django.db.models.fields.FloatField')(default=0.1)),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('bet_number', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('open_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('issue_number', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('win_number', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('prize', self.gf('django.db.models.fields.FloatField')(null=True)),
        ))
        db.send_create_signal(u'wanglibao_lottery', ['Lottery'])


    def backwards(self, orm):
        # Deleting model 'Lottery'
        db.delete_table(u'wanglibao_lottery_lottery')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'wanglibao_lottery.lottery': {
            'Meta': {'object_name': 'Lottery'},
            'bet_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'buy_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'count': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue_number': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'lottery_type': ('django.db.models.fields.CharField', [], {'default': "'\\xe5\\x8f\\x8c\\xe8\\x89\\xb2\\xe7\\x90\\x83'", 'max_length': '50'}),
            'money_type': ('django.db.models.fields.FloatField', [], {'default': '0.1'}),
            'open_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'prize': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'lottery'", 'to': u"orm['auth.User']"}),
            'win_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'})
        }
    }

    complete_apps = ['wanglibao_lottery']