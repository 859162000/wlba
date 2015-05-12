# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AutomaticPlan'
        db.create_table(u'wanglibao_p2p_automaticplan', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='plan_user', to=orm['auth.User'])),
            ('amounts_auto', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=20, decimal_places=2)),
            ('amounts_left', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=20, decimal_places=2)),
            ('period_min', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('period_max', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('rate_min', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('rate_max', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('create_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('is_used', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'wanglibao_p2p', ['AutomaticPlan'])

        # Adding field 'P2PRecord.platform'
        db.add_column(u'wanglibao_p2p_p2precord', 'platform',
                      self.gf('django.db.models.fields.CharField')(default=u'', max_length=100),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'AutomaticPlan'
        db.delete_table(u'wanglibao_p2p_automaticplan')

        # Deleting field 'P2PRecord.platform'
        db.delete_column(u'wanglibao_p2p_p2precord', 'platform')


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
        u'marketing.activity': {
            'Meta': {'ordering': "['-create_time']", 'object_name': 'Activity'},
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'rule': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['marketing.ActivityRule']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'marketing.activityrule': {
            'Meta': {'ordering': "['-create_time']", 'object_name': 'ActivityRule'},
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'rule_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '4'}),
            'rule_type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'})
        },
        u'wanglibao_p2p.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.P2PProduct']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'wanglibao_p2p.automaticplan': {
            'Meta': {'object_name': 'AutomaticPlan'},
            'amounts_auto': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'amounts_left': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'create_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_used': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'period_max': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'period_min': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rate_max': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'rate_min': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'plan_user'", 'to': u"orm['auth.User']"})
        },
        u'wanglibao_p2p.contracttemplate': {
            'Meta': {'object_name': 'ContractTemplate'},
            'content': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'content_preview': ('django.db.models.fields.TextField', [], {'default': "''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'wanglibao_p2p.earning': {
            'Meta': {'ordering': "['-create_time']", 'object_name': 'Earning'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'confirm_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'margin_record': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_margin.MarginRecord']", 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['order.Order']", 'null': 'True', 'blank': 'True'}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['wanglibao_p2p.P2PProduct']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'D'", 'max_length': '5'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
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
        u'wanglibao_p2p.interestinadvance': {
            'Meta': {'ordering': "['-id']", 'object_name': 'InterestInAdvance'},
            'amount': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'create_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'days': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.P2PProduct']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'product_soldout_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'product_year_rate': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'subscription_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'})
        },
        u'wanglibao_p2p.interestprecisionbalance': {
            'Meta': {'ordering': "['-create_time']", 'object_name': 'InterestPrecisionBalance'},
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'equity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'interest_precision_balance'", 'null': 'True', 'to': u"orm['wanglibao_p2p.P2PEquity']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest_actual': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'interest_precision_balance': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '8'}),
            'interest_receivable': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '8'}),
            'principal': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'})
        },
        u'wanglibao_p2p.p2pcontract': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'P2PContract'},
            'contract_path': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'equity': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'equity_contract'", 'unique': 'True', 'null': 'True', 'to': u"orm['wanglibao_p2p.P2PEquity']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'wanglibao_p2p.p2pequity': {
            'Meta': {'ordering': "('-created_at',)", 'unique_together': "(('user', 'product'),)", 'object_name': 'P2PEquity'},
            'confirm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'confirm_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'contract': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'equity': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'equities'", 'to': u"orm['wanglibao_p2p.P2PProduct']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'equities'", 'to': u"orm['auth.User']"}),
            'version': ('concurrency.fields.IntegerVersionField', [], {'name': "'version'", 'db_tablespace': "''"})
        },
        u'wanglibao_p2p.p2pequityjiuxian': {
            'Meta': {'ordering': "('-created_at',)", 'unique_together': "(('user', 'product'),)", 'object_name': 'P2PEquityJiuxian'},
            'confirm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'confirm_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'equity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'equity_jiuxian'", 'to': u"orm['wanglibao_p2p.P2PEquity']"}),
            'equity_amount': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'equity_jiuxian_p2p'", 'to': u"orm['wanglibao_p2p.P2PProduct']"}),
            'selected_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'selected_type': ('django.db.models.fields.CharField', [], {'default': "'principal'", 'max_length': '20'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'equity_jiuxian_user'", 'to': u"orm['auth.User']"})
        },
        u'wanglibao_p2p.p2pproduct': {
            'Meta': {'object_name': 'P2PProduct'},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['marketing.Activity']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'amortization_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'baoli_original_contract_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'baoli_original_contract_number': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'baoli_trade_relation': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'borrower_address': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'borrower_bankcard': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'borrower_bankcard_bank_branch': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'borrower_bankcard_bank_city': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'borrower_bankcard_bank_code': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'borrower_bankcard_bank_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'borrower_bankcard_bank_province': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'borrower_bankcard_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'borrower_id_number': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'borrower_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'borrower_phone': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'bought_amount': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'bought_amount_random': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'bought_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'bought_count_random': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'bought_people_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'brief': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'default': "u'\\u666e\\u901a'", 'max_length': '16'}),
            'contract_serial_number': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'contract_template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.ContractTemplate']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 5, 19, 0, 0)'}),
            'excess_earning_description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'excess_earning_rate': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'expected_earning_rate': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'extra_data': ('wanglibao.fields.JSONFieldUtf8', [], {'blank': 'True'}),
            'hide': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit_per_user': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'make_loans_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ordered_amount': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'pay_method': ('django.db.models.fields.CharField', [], {'default': "u'\\u7b49\\u989d\\u672c\\u606f'", 'max_length': '32'}),
            'period': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'publish_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'repaying_source': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'serial_number': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True', 'null': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'short_usage': ('django.db.models.fields.TextField', [], {}),
            'soldout_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'\\u5f55\\u6807'", 'max_length': '16'}),
            'total_amount': ('django.db.models.fields.BigIntegerField', [], {'default': '1'}),
            'usage': ('django.db.models.fields.TextField', [], {}),
            'version': ('concurrency.fields.IntegerVersionField', [], {'name': "'version'", 'db_tablespace': "''"}),
            'warrant_company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.WarrantCompany']"})
        },
        u'wanglibao_p2p.p2pproductcontract': {
            'Meta': {'ordering': "['-id']", 'object_name': 'P2PProductContract'},
            'bill_accepting_bank': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'bill_amount': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'bill_drawer_bank': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'bill_due_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'bill_number': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'party_b': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'party_b_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'party_b_type': ('django.db.models.fields.CharField', [], {'default': "u'\\u4f01\\u4e1a'", 'max_length': '16'}),
            'party_c': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'}),
            'party_c_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'}),
            'party_c_id_number': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'party_c_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32'}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'default': "''", 'to': u"orm['wanglibao_p2p.P2PProduct']", 'unique': 'True'}),
            'signing_date': ('django.db.models.fields.DateField', [], {})
        },
        u'wanglibao_p2p.p2precord': {
            'Meta': {'ordering': "['-create_time']", 'object_name': 'P2PRecord'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'catalog': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'platform': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '100'}),
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
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'amortizations'", 'null': 'True', 'to': u"orm['wanglibao_p2p.P2PProduct']"}),
            'ready_for_settle': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'settled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'settlement_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'term': ('django.db.models.fields.IntegerField', [], {}),
            'term_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'version': ('concurrency.fields.IntegerVersionField', [], {'name': "'version'", 'db_tablespace': "''"})
        },
        u'wanglibao_p2p.productinterestprecision': {
            'Meta': {'ordering': "['-create_time']", 'object_name': 'ProductInterestPrecision'},
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest_actual': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'interest_precision_balance': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '8'}),
            'interest_receivable': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '8'}),
            'principal': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'interest_precision_balance'", 'null': 'True', 'to': u"orm['wanglibao_p2p.P2PProduct']"})
        },
        u'wanglibao_p2p.useramortization': {
            'Meta': {'ordering': "['user', 'term']", 'object_name': 'UserAmortization'},
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'penal_interest': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '20', 'decimal_places': '2'}),
            'principal': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'product_amortization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subs'", 'to': u"orm['wanglibao_p2p.ProductAmortization']"}),
            'settled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'settlement_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'term': ('django.db.models.fields.IntegerField', [], {}),
            'term_date': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'version': ('concurrency.fields.IntegerVersionField', [], {'name': "'version'", 'db_tablespace': "''"})
        },
        u'wanglibao_p2p.warrant': {
            'Meta': {'object_name': 'Warrant'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
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