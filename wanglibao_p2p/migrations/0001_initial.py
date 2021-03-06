# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'WarrantCompany'
        db.create_table(u'wanglibao_p2p_warrantcompany', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'wanglibao_p2p', ['WarrantCompany'])

        # Adding model 'P2PProductPayment'
        db.create_table(u'wanglibao_p2p_p2pproductpayment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.CharField')(default=u'', max_length=1000, blank=u'')),
            ('catalog_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'wanglibao_p2p', ['P2PProductPayment'])

        # Adding model 'P2PProduct'
        db.create_table(u'wanglibao_p2p_p2pproduct', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bought_people_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('bought_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('bought_amount', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('bought_count_random', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('bought_amount_random', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('status', self.gf('django.db.models.fields.CharField')(default=u'\u6b63\u5728\u62db\u6807', max_length=16)),
            ('period', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('brief', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('expected_earning_rate', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('closed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('payment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_p2p.P2PProductPayment'], null=True)),
            ('total_amount', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('ordered_amount', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('extra_data', self.gf('jsonfield.fields.JSONField')(blank=True)),
            ('publish_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('limit_per_user', self.gf('django.db.models.fields.FloatField')(default=0.2)),
            ('warrant_company', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_p2p.WarrantCompany'])),
            ('usage', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('short_usage', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'wanglibao_p2p', ['P2PProduct'])

        # Adding model 'Warrant'
        db.create_table(u'wanglibao_p2p_warrant', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('warranted_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_p2p.P2PProduct'])),
        ))
        db.send_create_signal(u'wanglibao_p2p', ['Warrant'])

        # Adding model 'ProductAmortization'
        db.create_table(u'wanglibao_p2p_productamortization', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='amortizations', to=orm['wanglibao_p2p.P2PProduct'])),
            ('term', self.gf('django.db.models.fields.IntegerField')()),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('penal_interest', self.gf('django.db.models.fields.DecimalField')(default='0', max_digits=20, decimal_places=2)),
            ('delay', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('settled', self.gf('django.db.models.fields.BooleanField')()),
            ('settlement_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'wanglibao_p2p', ['ProductAmortization'])

        # Adding model 'ProductUserAmortization'
        db.create_table(u'wanglibao_p2p_productuseramortization', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('amortization', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'to_users', to=orm['wanglibao_p2p.ProductAmortization'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('current_equity', self.gf('django.db.models.fields.BigIntegerField')()),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000)),
        ))
        db.send_create_signal(u'wanglibao_p2p', ['ProductUserAmortization'])

        # Adding model 'P2PRecord'
        db.create_table(u'wanglibao_p2p_p2precord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('catalog', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('order_id', self.gf('django.db.models.fields.IntegerField')()),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_p2p.P2PProduct'], null=True)),
            ('product_balance_after', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('user_margin_after', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=20, decimal_places=2)),
            ('operation_ip', self.gf('django.db.models.fields.IPAddressField')(default='', max_length=15)),
            ('operation_request_headers', self.gf('django.db.models.fields.TextField')(default='', max_length=1000)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=1000)),
        ))
        db.send_create_signal(u'wanglibao_p2p', ['P2PRecord'])

        # Adding model 'P2PEquity'
        db.create_table(u'wanglibao_p2p_p2pequity', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='equities', to=orm['auth.User'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='equities', to=orm['wanglibao_p2p.P2PProduct'])),
            ('equity', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('confirm', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'wanglibao_p2p', ['P2PEquity'])

        # Adding unique constraint on 'P2PEquity', fields ['user', 'product']
        db.create_unique(u'wanglibao_p2p_p2pequity', ['user_id', 'product_id'])

        # Adding model 'EquityRecord'
        db.create_table(u'wanglibao_p2p_equityrecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('catalog', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_p2p.P2PProduct'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('description', self.gf('django.db.models.fields.CharField')(default=u'', max_length=1000)),
            ('checksum', self.gf('django.db.models.fields.CharField')(default=u'', max_length=1000)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'wanglibao_p2p', ['EquityRecord'])


    def backwards(self, orm):
        # Removing unique constraint on 'P2PEquity', fields ['user', 'product']
        db.delete_unique(u'wanglibao_p2p_p2pequity', ['user_id', 'product_id'])

        # Deleting model 'WarrantCompany'
        db.delete_table(u'wanglibao_p2p_warrantcompany')

        # Deleting model 'P2PProductPayment'
        db.delete_table(u'wanglibao_p2p_p2pproductpayment')

        # Deleting model 'P2PProduct'
        db.delete_table(u'wanglibao_p2p_p2pproduct')

        # Deleting model 'Warrant'
        db.delete_table(u'wanglibao_p2p_warrant')

        # Deleting model 'ProductAmortization'
        db.delete_table(u'wanglibao_p2p_productamortization')

        # Deleting model 'ProductUserAmortization'
        db.delete_table(u'wanglibao_p2p_productuseramortization')

        # Deleting model 'P2PRecord'
        db.delete_table(u'wanglibao_p2p_p2precord')

        # Deleting model 'P2PEquity'
        db.delete_table(u'wanglibao_p2p_p2pequity')

        # Deleting model 'EquityRecord'
        db.delete_table(u'wanglibao_p2p_equityrecord')


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
            'catalog': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'checksum': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '1000'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.P2PProduct']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'wanglibao_p2p.p2pequity': {
            'Meta': {'unique_together': "(('user', 'product'),)", 'object_name': 'P2PEquity'},
            'confirm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'equity': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'equities'", 'to': u"orm['wanglibao_p2p.P2PProduct']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'equities'", 'to': u"orm['auth.User']"})
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
        u'wanglibao_p2p.p2precord': {
            'Meta': {'ordering': "['-create_time']", 'object_name': 'P2PRecord'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'catalog': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'operation_ip': ('django.db.models.fields.IPAddressField', [], {'default': "''", 'max_length': '15'}),
            'operation_request_headers': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '1000'}),
            'order_id': ('django.db.models.fields.IntegerField', [], {}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.P2PProduct']", 'null': 'True'}),
            'product_balance_after': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            'user_margin_after': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '2'})
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
            'current_equity': ('django.db.models.fields.BigIntegerField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
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