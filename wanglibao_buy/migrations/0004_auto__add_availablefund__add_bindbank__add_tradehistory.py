# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AvailableFund'
        db.create_table(u'wanglibao_buy_availablefund', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('declare_status', self.gf('django.db.models.fields.BooleanField')()),
            ('fund_code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('fund_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('fund_state', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('fund_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('last_update', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('min_shares', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('purchase_limit_max', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('purchase_limit_min', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('purchase_second_limit_min', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('quick_cash_limit_max', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('quick_cash_limit_min', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('ration_limit_max', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('ration_limit_min', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('redeem_limit_max', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('redeem_limit_min', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('risk_level', self.gf('django.db.models.fields.IntegerField')()),
            ('share_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('subscribe_limit_max', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('subscribe_limit_min', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('subscribe_state', self.gf('django.db.models.fields.BooleanField')()),
            ('transform_limit_max', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('transform_limit_min', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('valuagr_state', self.gf('django.db.models.fields.BooleanField')()),
            ('withdraw_state', self.gf('django.db.models.fields.BooleanField')()),
            ('create_date', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'wanglibao_buy', ['AvailableFund'])

        # Adding model 'BindBank'
        db.create_table(u'wanglibao_buy_bindbank', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('no', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('balance', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('bank_name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('bank_serial', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('bind_way', self.gf('django.db.models.fields.IntegerField')()),
            ('capital_mode', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('content_describe', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('is_freeze', self.gf('django.db.models.fields.BooleanField')()),
            ('is_vaild', self.gf('django.db.models.fields.BooleanField')()),
            ('limit_describe', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('priority', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('status_to_cn', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('sub_trade_account', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('support_auto_pay', self.gf('django.db.models.fields.BooleanField')()),
            ('trade_account', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('create_date', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'wanglibao_buy', ['BindBank'])

        # Adding model 'TradeHistory'
        db.create_table(u'wanglibao_buy_tradehistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('apply_date_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('apply_serial', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('bank_account', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('bank_name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('bank_serial', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('business_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('business_type_to_cn', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('can_cancel', self.gf('django.db.models.fields.BooleanField')()),
            ('fund_code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('fund_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('is_cash_buy', self.gf('django.db.models.fields.BooleanField')()),
            ('pay_result', self.gf('django.db.models.fields.IntegerField')()),
            ('pay_status_to_cn', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('pound_age', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('share_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('share_type_to_cn', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('shares', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('status', self.gf('django.db.models.fields.IntegerField')()),
            ('status_to_cn', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('trade_account', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('create_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'wanglibao_buy', ['TradeHistory'])


    def backwards(self, orm):
        # Deleting model 'AvailableFund'
        db.delete_table(u'wanglibao_buy_availablefund')

        # Deleting model 'BindBank'
        db.delete_table(u'wanglibao_buy_bindbank')

        # Deleting model 'TradeHistory'
        db.delete_table(u'wanglibao_buy_tradehistory')


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
        u'wanglibao_buy.availablefund': {
            'Meta': {'object_name': 'AvailableFund'},
            'create_date': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'declare_status': ('django.db.models.fields.BooleanField', [], {}),
            'fund_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'fund_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'fund_state': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'fund_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'min_shares': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'purchase_limit_max': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'purchase_limit_min': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'purchase_second_limit_min': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'quick_cash_limit_max': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'quick_cash_limit_min': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'ration_limit_max': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'ration_limit_min': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'redeem_limit_max': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'redeem_limit_min': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'risk_level': ('django.db.models.fields.IntegerField', [], {}),
            'share_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'subscribe_limit_max': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'subscribe_limit_min': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'subscribe_state': ('django.db.models.fields.BooleanField', [], {}),
            'transform_limit_max': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'transform_limit_min': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'valuagr_state': ('django.db.models.fields.BooleanField', [], {}),
            'withdraw_state': ('django.db.models.fields.BooleanField', [], {})
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
        u'wanglibao_buy.fundholdinfo': {
            'Meta': {'object_name': 'FundHoldInfo'},
            'bank_account': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'bank_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'bank_serial': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'capital_mode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'create_date': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'current_remain_share': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'expire_shares': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'freeze_remain_share': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'fund_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'fund_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'fund_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'fund_type_to_cn': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'market_value': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '3'}),
            'melon_method': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'nav_date': ('django.db.models.fields.DateField', [], {}),
            'pernet_value': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'rapid_redeem': ('django.db.models.fields.BooleanField', [], {}),
            'share_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            't_freeze_remain_share': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'trade_account': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'unpaid_income': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'usable_remain_share': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'wanglibao_buy.tradehistory': {
            'Meta': {'object_name': 'TradeHistory'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'apply_date_time': ('django.db.models.fields.DateTimeField', [], {}),
            'apply_serial': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'bank_account': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'bank_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'bank_serial': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'business_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'business_type_to_cn': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'can_cancel': ('django.db.models.fields.BooleanField', [], {}),
            'create_date': ('django.db.models.fields.DateField', [], {}),
            'fund_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'fund_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_cash_buy': ('django.db.models.fields.BooleanField', [], {}),
            'pay_result': ('django.db.models.fields.IntegerField', [], {}),
            'pay_status_to_cn': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'pound_age': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'share_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'share_type_to_cn': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'shares': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'status_to_cn': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'trade_account': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'wanglibao_buy.tradeinfo': {
            'Meta': {'object_name': 'TradeInfo'},
            'amount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_id': ('django.db.models.fields.IntegerField', [], {}),
            'item_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'related_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'trade_type': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'verify_info': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        }
    }

    complete_apps = ['wanglibao_buy']