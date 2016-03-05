# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PayInfo'
        db.create_table(u'wanglibao_pay_payinfo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('uuid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32, db_index=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('fee', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=20, decimal_places=2)),
            ('management_fee', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=20, decimal_places=2)),
            ('management_amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=20, decimal_places=2)),
            ('total_amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=20, decimal_places=2)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('update_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('confirm_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('user', self.gf('django.db.models.fields.IntegerField')(max_length=50)),
            ('order', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('margin_record', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'wanglibao_pay', ['PayInfo'])


    def backwards(self, orm):
        # Deleting model 'PayInfo'
        db.delete_table(u'wanglibao_pay_payinfo')


    models = {
        u'wanglibao_pay.payinfo': {
            'Meta': {'ordering': "['-create_time']", 'object_name': 'PayInfo'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'confirm_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'fee': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'management_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'management_fee': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'margin_record': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'total_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.IntegerField', [], {'max_length': '50'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'})
        }
    }

    complete_apps = ['wanglibao_pay']