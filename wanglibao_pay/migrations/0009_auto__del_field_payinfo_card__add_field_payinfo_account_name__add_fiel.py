# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'PayInfo.card'
        db.delete_column(u'wanglibao_pay_payinfo', 'card_id')

        # Adding field 'PayInfo.account_name'
        db.add_column(u'wanglibao_pay_payinfo', 'account_name',
                      self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True),
                      keep_default=False)

        # Adding field 'PayInfo.card_no'
        db.add_column(u'wanglibao_pay_payinfo', 'card_no',
                      self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True),
                      keep_default=False)


        # Changing field 'PayInfo.user'
        db.alter_column(u'wanglibao_pay_payinfo', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], on_delete=models.PROTECT))

        # Changing field 'PayInfo.bank'
        db.alter_column(u'wanglibao_pay_payinfo', 'bank_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_pay.Bank'], null=True, on_delete=models.PROTECT))

        # Changing field 'Card.bank'
        db.alter_column(u'wanglibao_pay_card', 'bank_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_pay.Bank'], on_delete=models.PROTECT))

    def backwards(self, orm):
        # Adding field 'PayInfo.card'
        db.add_column(u'wanglibao_pay_payinfo', 'card',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_pay.Card'], null=True, blank=True),
                      keep_default=False)

        # Deleting field 'PayInfo.account_name'
        db.delete_column(u'wanglibao_pay_payinfo', 'account_name')

        # Deleting field 'PayInfo.card_no'
        db.delete_column(u'wanglibao_pay_payinfo', 'card_no')


        # Changing field 'PayInfo.user'
        db.alter_column(u'wanglibao_pay_payinfo', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

        # Changing field 'PayInfo.bank'
        db.alter_column(u'wanglibao_pay_payinfo', 'bank_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_pay.Bank'], null=True))

        # Changing field 'Card.bank'
        db.alter_column(u'wanglibao_pay_card', 'bank_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_pay.Bank']))

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
        u'order.order': {
            'Meta': {'object_name': 'Order'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'extra_data': ('wanglibao.fields.JSONFieldUtf8', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': u"orm['order.Order']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'wanglibao_margin.marginrecord': {
            'Meta': {'ordering': "['-create_time']", 'object_name': 'MarginRecord'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'catalog': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'margin_current': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'order_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'})
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
        u'wanglibao_pay.card': {
            'Meta': {'object_name': 'Card'},
            'add_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'bank': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_pay.Bank']", 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'no': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'wanglibao_pay.payinfo': {
            'Meta': {'ordering': "['-create_time']", 'object_name': 'PayInfo'},
            'account_name': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'bank': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_pay.Bank']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'card_no': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'error_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'error_message': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'fee': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'margin_record': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_margin.MarginRecord']", 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['order.Order']", 'null': 'True', 'blank': 'True'}),
            'request': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'request_ip': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'response': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'response_ip': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'total_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'on_delete': 'models.PROTECT'})
        }
    }

    complete_apps = ['wanglibao_pay']