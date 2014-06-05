# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Bank'
        db.create_table(u'wanglibao_buy_bank', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('threshold_info', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'wanglibao_buy', ['Bank'])


    def backwards(self, orm):
        # Deleting model 'Bank'
        db.delete_table(u'wanglibao_buy_bank')


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
            'fund': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['wanglibao_fund.Fund']", 'unique': 'True', 'null': 'True'}),
            'fund_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'fund_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'fund_state': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'fund_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {}),
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
        u'wanglibao_buy.bank': {
            'Meta': {'object_name': 'Bank'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'threshold_info': ('django.db.models.fields.TextField', [], {})
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
        u'wanglibao_buy.dailyincome': {
            'Meta': {'ordering': "['-date']", 'unique_together': "(('user', 'date'),)", 'object_name': 'DailyIncome'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'income': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '5'}),
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
        u'wanglibao_buy.monetaryfundnetvalue': {
            'Meta': {'ordering': "['-curr_date']", 'unique_together': "(('code', 'curr_date'),)", 'object_name': 'MonetaryFundNetValue'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'create_date': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'curr_date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'income_per_ten_thousand': ('django.db.models.fields.FloatField', [], {})
        },
        u'wanglibao_buy.tradehistory': {
            'Meta': {'ordering': "['-apply_date_time']", 'object_name': 'TradeHistory'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'apply_date_time': ('django.db.models.fields.DateTimeField', [], {}),
            'apply_serial': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'bank_account': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'bank_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'bank_serial': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'business_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'business_type_to_cn': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'can_cancel': ('django.db.models.fields.BooleanField', [], {}),
            'create_date': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
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
        },
        u'wanglibao_fund.fund': {
            'Meta': {'object_name': 'Fund'},
            'accumulated_face_value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'bought_amount': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'bought_amount_random': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'bought_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'bought_count_random': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'bought_people_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'brief': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'earned_per_10k': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'face_value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'found_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'hosting_bank': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'hosting_fee': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'init_scale': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'invest_risk': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'investment_scope': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'investment_strategy': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'investment_target': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'investment_threshold': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'issuer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_fund.FundIssuer']"}),
            'latest_scale': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'latest_shares': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'management_fee': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'manager': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'product_code': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'profit_allocation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'profit_month': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'rate_1_month': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'rate_1_week': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'rate_1_year': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'rate_3_months': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'rate_6_months': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'rate_7_days': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'rate_today': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'risk_character': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'trade_status': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'})
        },
        u'wanglibao_fund.fundissuer': {
            'Meta': {'object_name': 'FundIssuer'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'home_page': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64'}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'})
        }
    }

    complete_apps = ['wanglibao_buy']