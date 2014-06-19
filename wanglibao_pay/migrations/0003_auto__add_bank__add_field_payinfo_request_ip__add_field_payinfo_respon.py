# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Bank'
        db.create_table(u'wanglibao_pay_bank', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('gate_id', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('limit', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('sort_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'wanglibao_pay', ['Bank'])

        # Adding field 'PayInfo.request_ip'
        db.add_column(u'wanglibao_pay_payinfo', 'request_ip',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'PayInfo.response_ip'
        db.add_column(u'wanglibao_pay_payinfo', 'response_ip',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'PayInfo.card'
        db.add_column(u'wanglibao_pay_payinfo', 'card',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_buy.BindBank'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Bank'
        db.delete_table(u'wanglibao_pay_bank')

        # Deleting field 'PayInfo.request_ip'
        db.delete_column(u'wanglibao_pay_payinfo', 'request_ip')

        # Deleting field 'PayInfo.response_ip'
        db.delete_column(u'wanglibao_pay_payinfo', 'response_ip')

        # Deleting field 'PayInfo.card'
        db.delete_column(u'wanglibao_pay_payinfo', 'card_id')


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
        u'wanglibao_buy.bindbank': {
            'Meta': {'object_name': 'BindBank'},
            'balance': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'bank_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'bank_serial': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'bind_way': ('django.db.models.fields.IntegerField', [], {}),
            'capital_mode': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'content_describe': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'create_date': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_freeze': ('django.db.models.fields.BooleanField', [], {}),
            'is_vaild': ('django.db.models.fields.BooleanField', [], {}),
            'limit_describe': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'no': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'priority': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'status_to_cn': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'sub_trade_account': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'support_auto_pay': ('django.db.models.fields.BooleanField', [], {}),
            'trade_account': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'wanglibao_pay.bank': {
            'Meta': {'ordering': "('-sort_order',)", 'object_name': 'Bank'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'gate_id': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'wanglibao_pay.payinfo': {
            'Meta': {'object_name': 'PayInfo'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'card': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_buy.BindBank']", 'null': 'True', 'blank': 'True'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'error_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'error_message': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'request': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'request_ip': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'response': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'response_ip': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['wanglibao_pay']