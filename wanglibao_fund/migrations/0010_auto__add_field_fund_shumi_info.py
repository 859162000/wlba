# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Fund.shumi_info'
        db.add_column(u'wanglibao_fund_fund', 'shumi_info',
                      self.gf('django.db.models.fields.related.OneToOneField')(to=orm['wanglibao_buy.AvailableFund'], unique=True, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Fund.shumi_info'
        db.delete_column(u'wanglibao_fund_fund', 'shumi_info_id')


    models = {
        u'wanglibao_buy.availablefund': {
            'Meta': {'object_name': 'AvailableFund'},
            'create_date': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'declare_status': ('django.db.models.fields.BooleanField', [], {}),
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
        u'wanglibao_fund.fund': {
            'Meta': {'object_name': 'Fund'},
            'accumulated_face_value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'bought_amount': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'bought_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
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
            'shumi_info': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['wanglibao_buy.AvailableFund']", 'unique': 'True', 'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'trade_status': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'})
        },
        u'wanglibao_fund.fundissuer': {
            'Meta': {'object_name': 'FundIssuer'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'home_page': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'wanglibao_fund.issuebackendchargerate': {
            'Meta': {'object_name': 'IssueBackEndChargeRate'},
            'bottom_line': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'fund': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'issue_back_end_charge_rates'", 'to': u"orm['wanglibao_fund.Fund']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'top_line': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'value_type': ('django.db.models.fields.CharField', [], {'default': "'percent'", 'max_length': '8'})
        },
        u'wanglibao_fund.issuefrontendchargerate': {
            'Meta': {'object_name': 'IssueFrontEndChargeRate'},
            'bottom_line': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'fund': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'issue_front_end_charge_rates'", 'to': u"orm['wanglibao_fund.Fund']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'top_line': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'value_type': ('django.db.models.fields.CharField', [], {'default': "'percent'", 'max_length': '8'})
        },
        u'wanglibao_fund.redeembackendchargerate': {
            'Meta': {'object_name': 'RedeemBackEndChargeRate'},
            'bottom_line': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'fund': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'redeem_back_end_charge_rates'", 'to': u"orm['wanglibao_fund.Fund']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'top_line': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'value_type': ('django.db.models.fields.CharField', [], {'default': "'percent'", 'max_length': '8'})
        },
        u'wanglibao_fund.redeemfrontendchargerate': {
            'Meta': {'object_name': 'RedeemFrontEndChargeRate'},
            'bottom_line': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'fund': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'redeem_front_end_charge_rates'", 'to': u"orm['wanglibao_fund.Fund']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'top_line': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'value_type': ('django.db.models.fields.CharField', [], {'default': "'percent'", 'max_length': '8'})
        }
    }

    complete_apps = ['wanglibao_fund']