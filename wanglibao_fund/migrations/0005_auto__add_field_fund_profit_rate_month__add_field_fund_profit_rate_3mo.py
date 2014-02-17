# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Fund.profit_rate_month'
        db.add_column(u'wanglibao_fund_fund', 'profit_rate_month',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.profit_rate_3months'
        db.add_column(u'wanglibao_fund_fund', 'profit_rate_3months',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.profit_rate_6months'
        db.add_column(u'wanglibao_fund_fund', 'profit_rate_6months',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Fund.profit_rate_month'
        db.delete_column(u'wanglibao_fund_fund', 'profit_rate_month')

        # Deleting field 'Fund.profit_rate_3months'
        db.delete_column(u'wanglibao_fund_fund', 'profit_rate_3months')

        # Deleting field 'Fund.profit_rate_6months'
        db.delete_column(u'wanglibao_fund_fund', 'profit_rate_6months')


    models = {
        u'wanglibao_fund.fund': {
            'AIP_able': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'Meta': {'object_name': 'Fund'},
            'accumulated_face_value': ('django.db.models.fields.FloatField', [], {}),
            'brief': ('django.db.models.fields.TextField', [], {}),
            'earned_per_10k': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'face_value': ('django.db.models.fields.FloatField', [], {}),
            'frontend_hosting_charge_rate': ('django.db.models.fields.FloatField', [], {}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'fund_date': ('django.db.models.fields.DateField', [], {}),
            'hosted_bank': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'hosted_bank_description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invest_scope': ('django.db.models.fields.TextField', [], {}),
            'invest_target': ('django.db.models.fields.TextField', [], {}),
            'issuable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'issuer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_fund.FundIssuer']"}),
            'management_charge_rate': ('django.db.models.fields.FloatField', [], {}),
            'manager': ('django.db.models.fields.TextField', [], {}),
            'mode': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'performance_compare_baseline': ('django.db.models.fields.TextField', [], {}),
            'portfolio': ('django.db.models.fields.TextField', [], {}),
            'product_code': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'profit_per_month': ('django.db.models.fields.FloatField', [], {}),
            'profit_rate_3months': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'profit_rate_6months': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'profit_rate_7days': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'profit_rate_month': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'rate_day': ('django.db.models.fields.FloatField', [], {}),
            'redeemable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sales_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'scale': ('django.db.models.fields.FloatField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        u'wanglibao_fund.fundissuer': {
            'Meta': {'object_name': 'FundIssuer'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'home_page': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'wanglibao_fund.issuebackendchargerate': {
            'Meta': {'object_name': 'IssueBackEndChargeRate'},
            'bottom_line': ('django.db.models.fields.FloatField', [], {}),
            'fund': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'issue_back_end_charge_rates'", 'to': u"orm['wanglibao_fund.Fund']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'top_line': ('django.db.models.fields.FloatField', [], {}),
            'value': ('django.db.models.fields.FloatField', [], {}),
            'value_type': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        u'wanglibao_fund.issuefrontendchargerate': {
            'Meta': {'object_name': 'IssueFrontEndChargeRate'},
            'bottom_line': ('django.db.models.fields.FloatField', [], {}),
            'fund': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'issue_front_end_charge_rates'", 'to': u"orm['wanglibao_fund.Fund']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'top_line': ('django.db.models.fields.FloatField', [], {}),
            'value': ('django.db.models.fields.FloatField', [], {}),
            'value_type': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        u'wanglibao_fund.redeembackendchargerate': {
            'Meta': {'object_name': 'RedeemBackEndChargeRate'},
            'bottom_line': ('django.db.models.fields.FloatField', [], {}),
            'fund': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'redeem_back_end_charge_rates'", 'to': u"orm['wanglibao_fund.Fund']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'top_line': ('django.db.models.fields.FloatField', [], {}),
            'value': ('django.db.models.fields.FloatField', [], {}),
            'value_type': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        u'wanglibao_fund.redeemfrontendchargerate': {
            'Meta': {'object_name': 'RedeemFrontEndChargeRate'},
            'bottom_line': ('django.db.models.fields.FloatField', [], {}),
            'fund': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'redeem_front_end_charge_rates'", 'to': u"orm['wanglibao_fund.Fund']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'top_line': ('django.db.models.fields.FloatField', [], {}),
            'value': ('django.db.models.fields.FloatField', [], {}),
            'value_type': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        }
    }

    complete_apps = ['wanglibao_fund']