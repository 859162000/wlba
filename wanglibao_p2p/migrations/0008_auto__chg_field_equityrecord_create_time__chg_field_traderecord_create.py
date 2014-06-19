# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'EquityRecord.create_time'
        db.alter_column(u'wanglibao_p2p_equityrecord', 'create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

        # Changing field 'TradeRecord.create_time'
        db.alter_column(u'wanglibao_p2p_traderecord', 'create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))
        # Adding field 'MarginRecord.amount'
        db.add_column(u'wanglibao_p2p_marginrecord', 'amount',
                      self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=20, decimal_places=2),
                      keep_default=False)


        # Changing field 'MarginRecord.create_time'
        db.alter_column(u'wanglibao_p2p_marginrecord', 'create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

    def backwards(self, orm):

        # Changing field 'EquityRecord.create_time'
        db.alter_column(u'wanglibao_p2p_equityrecord', 'create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True))

        # Changing field 'TradeRecord.create_time'
        db.alter_column(u'wanglibao_p2p_traderecord', 'create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True))
        # Deleting field 'MarginRecord.amount'
        db.delete_column(u'wanglibao_p2p_marginrecord', 'amount')


        # Changing field 'MarginRecord.create_time'
        db.alter_column(u'wanglibao_p2p_marginrecord', 'create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True))

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
        u'wanglibao_p2p.equityrecord': {
            'Meta': {'object_name': 'EquityRecord'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'catalog': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.RecordCatalog']"}),
            'checksum': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '1000'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.P2PProduct']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'wanglibao_p2p.marginrecord': {
            'Meta': {'object_name': 'MarginRecord'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'catalog': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.RecordCatalog']"}),
            'checksum': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'user_margin_after': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'user_margin_before': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'})
        },
        u'wanglibao_p2p.p2pproduct': {
            'Meta': {'object_name': 'P2PProduct'},
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
            'payment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.P2PProductPayment']", 'null': 'True'}),
            'period': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'publish_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'short_usage': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'\\u6b63\\u5728\\u62db\\u6807'", 'max_length': '16'}),
            'total_amount': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'usage': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'warrant_company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.WarrantCompany']"})
        },
        u'wanglibao_p2p.p2pproductpayment': {
            'Meta': {'object_name': 'P2PProductPayment'},
            'catalog_id': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '1000', 'blank': "u''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'wanglibao_p2p.productamortization': {
            'Meta': {'object_name': 'ProductAmortization'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'delay': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'penal_interest': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '20', 'decimal_places': '2'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'amortizations'", 'to': u"orm['wanglibao_p2p.P2PProduct']"}),
            'settled': ('django.db.models.fields.BooleanField', [], {}),
            'settlement_time': ('django.db.models.fields.DateTimeField', [], {}),
            'term': ('django.db.models.fields.IntegerField', [], {})
        },
        u'wanglibao_p2p.productuseramortization': {
            'Meta': {'object_name': 'ProductUserAmortization'},
            'amortization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'to_users'", 'to': u"orm['wanglibao_p2p.ProductAmortization']"}),
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'current_user_equity': ('django.db.models.fields.BigIntegerField', [], {}),
            'delay': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'penal_interest': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '20', 'decimal_places': '2'})
        },
        u'wanglibao_p2p.recordcatalog': {
            'Meta': {'object_name': 'RecordCatalog'},
            'catalog_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'wanglibao_p2p.traderecord': {
            'Meta': {'object_name': 'TradeRecord'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'cancelable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'catalog': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.RecordCatalog']"}),
            'checksum': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'operation_ip': ('django.db.models.fields.IPAddressField', [], {'default': "''", 'max_length': '15'}),
            'operation_request_headers': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '1000'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.P2PProduct']"}),
            'product_balance_after': ('django.db.models.fields.IntegerField', [], {}),
            'product_balance_before': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'user_margin_after': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'user_margin_before': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'})
        },
        u'wanglibao_p2p.userequity': {
            'Meta': {'unique_together': "(('user', 'product'),)", 'object_name': 'UserEquity'},
            'confirm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'equity': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'equities'", 'to': u"orm['wanglibao_p2p.P2PProduct']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'equities'", 'to': u"orm['auth.User']"})
        },
        u'wanglibao_p2p.usermargin': {
            'Meta': {'object_name': 'UserMargin'},
            'freeze': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '20', 'decimal_places': '2'}),
            'margin': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '20', 'decimal_places': '2'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'withdrawing': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '20', 'decimal_places': '2'})
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