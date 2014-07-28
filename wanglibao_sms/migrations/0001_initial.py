# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models, OperationalError


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PhoneValidateCode'
        try:
            db.create_table(u'wanglibao_sms_phonevalidatecode', (
                (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('phone', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
                ('validate_code', self.gf('django.db.models.fields.CharField')(max_length=6)),
                ('validate_type', self.gf('django.db.models.fields.CharField')(max_length=64)),
                ('is_validated', self.gf('django.db.models.fields.BooleanField')(default=False)),
                ('last_send_time', self.gf('django.db.models.fields.DateTimeField')()),
                ('code_send_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
                ('data', self.gf('django.db.models.fields.TextField')(default='')),
            ))
            db.send_create_signal(u'wanglibao_sms', ['PhoneValidateCode'])
        except OperationalError, e:
            print 'Table created, fake the migration'


    def backwards(self, orm):
        # Deleting model 'PhoneValidateCode'
        db.delete_table(u'wanglibao_sms_phonevalidatecode')


    models = {
        u'wanglibao_sms.phonevalidatecode': {
            'Meta': {'object_name': 'PhoneValidateCode'},
            'code_send_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_validated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_send_time': ('django.db.models.fields.DateTimeField', [], {}),
            'phone': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'validate_code': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'validate_type': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['wanglibao_sms']