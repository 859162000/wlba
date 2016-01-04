# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EnterpriseUserProfile'
        db.create_table(u'wanglibao_qiye_enterpriseuserprofile', (
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], primary_key=True)),
            ('company_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('business_license', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('registration_cert', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('certigier_name', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('certigier_phone', self.gf('django.db.models.fields.IntegerField')(max_length=64)),
            ('company_address', self.gf('django.db.models.fields.TextField')(max_length=255)),
            ('company_account', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('company_account_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('deposit_bank_province', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('deposit_bank_city', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('bank_branch_address', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('modify_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'wanglibao_qiye', ['EnterpriseUserProfile'])


    def backwards(self, orm):
        # Deleting model 'EnterpriseUserProfile'
        db.delete_table(u'wanglibao_qiye_enterpriseuserprofile')


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
        u'wanglibao_qiye.enterpriseuserprofile': {
            'Meta': {'object_name': 'EnterpriseUserProfile'},
            'bank_branch_address': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'business_license': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'certigier_name': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'certigier_phone': ('django.db.models.fields.IntegerField', [], {'max_length': '64'}),
            'company_account': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'company_account_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'company_address': ('django.db.models.fields.TextField', [], {'max_length': '255'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'deposit_bank_city': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'deposit_bank_province': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'modify_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'registration_cert': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'primary_key': 'True'})
        }
    }

    complete_apps = ['wanglibao_qiye']