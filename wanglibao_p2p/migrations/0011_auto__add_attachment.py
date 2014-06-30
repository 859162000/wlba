# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Attachment'
        db.create_table(u'wanglibao_p2p_attachment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_p2p.P2PProduct'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('extra_data', self.gf('jsonfield.fields.JSONField')()),
        ))
        db.send_create_signal(u'wanglibao_p2p', ['Attachment'])


    def backwards(self, orm):
        # Deleting model 'Attachment'
        db.delete_table(u'wanglibao_p2p_attachment')


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
        u'wanglibao_p2p.amortizationrecord': {
            'Meta': {'object_name': 'AmortizationRecord'},
            'amortization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'to_users'", 'to': u"orm['wanglibao_p2p.ProductAmortization']"}),
            'catalog': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'order_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'penal_interest': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'principal': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'term': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'wanglibao_p2p.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'extra_data': ('jsonfield.fields.JSONField', [], {}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.P2PProduct']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'wanglibao_p2p.equityrecord': {
            'Meta': {'object_name': 'EquityRecord'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'catalog': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.P2PProduct']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'})
        },
        u'wanglibao_p2p.p2pequity': {
            'Meta': {'unique_together': "(('user', 'product'),)", 'object_name': 'P2PEquity'},
            'confirm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'equity': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'next_amount': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '20', 'decimal_places': '2'}),
            'next_term': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'paid_interest': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '20', 'decimal_places': '2'}),
            'paid_principal': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '20', 'decimal_places': '2'}),
            'penal_interest': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '20', 'decimal_places': '2'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'equities'", 'to': u"orm['wanglibao_p2p.P2PProduct']"}),
            'term': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'total_interest': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '20', 'decimal_places': '2'}),
            'total_term': ('django.db.models.fields.IntegerField', [], {'default': '12'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'equities'", 'to': u"orm['auth.User']"})
        },
        u'wanglibao_p2p.p2pproduct': {
            'Meta': {'object_name': 'P2PProduct'},
            'amortization_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'bought_amount': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'bought_amount_random': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'bought_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'bought_count_random': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'bought_people_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'brief': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'expected_earning_rate': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'extra_data': ('jsonfield.fields.JSONField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit_per_user': ('django.db.models.fields.FloatField', [], {'default': '0.2'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ordered_amount': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'pay_method': ('django.db.models.fields.CharField', [], {'default': "u'\\u7b49\\u989d\\u672c\\u606f'", 'max_length': '32', 'blank': 'True'}),
            'period': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'publish_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'short_usage': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'\\u6b63\\u5728\\u62db\\u6807'", 'max_length': '16'}),
            'total_amount': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'usage': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'warrant_company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.WarrantCompany']"})
        },
        u'wanglibao_p2p.p2precord': {
            'Meta': {'ordering': "['-create_time']", 'object_name': 'P2PRecord'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'catalog': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.P2PProduct']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'product_balance_after': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'})
        },
        u'wanglibao_p2p.productamortization': {
            'Meta': {'ordering': "['term']", 'object_name': 'ProductAmortization'},
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'penal_interest': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '20', 'decimal_places': '2'}),
            'principal': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'amortizations'", 'to': u"orm['wanglibao_p2p.P2PProduct']"}),
            'ready_for_settle': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'settled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'settlement_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'term': ('django.db.models.fields.IntegerField', [], {}),
            'term_date': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'wanglibao_p2p.warrant': {
            'Meta': {'object_name': 'Warrant'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.P2PProduct']"}),
            'warranted_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'wanglibao_p2p.warrantcompany': {
            'Meta': {'object_name': 'WarrantCompany'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['wanglibao_p2p']