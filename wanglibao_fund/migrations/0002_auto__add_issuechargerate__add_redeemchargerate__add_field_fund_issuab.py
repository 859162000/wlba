# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'IssueChargeRate'
        db.create_table(u'wanglibao_fund_issuechargerate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fund', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_fund.Fund'])),
            ('bottom_line', self.gf('django.db.models.fields.FloatField')()),
            ('top_line', self.gf('django.db.models.fields.FloatField')()),
            ('line_type', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('value', self.gf('django.db.models.fields.FloatField')()),
            ('value_type', self.gf('django.db.models.fields.CharField')(max_length=8)),
        ))
        db.send_create_signal(u'wanglibao_fund', ['IssueChargeRate'])

        # Adding model 'RedeemChargeRate'
        db.create_table(u'wanglibao_fund_redeemchargerate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fund', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_fund.Fund'])),
            ('bottom_line', self.gf('django.db.models.fields.FloatField')()),
            ('top_line', self.gf('django.db.models.fields.FloatField')()),
            ('line_type', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('value', self.gf('django.db.models.fields.FloatField')()),
            ('value_type', self.gf('django.db.models.fields.CharField')(max_length=8)),
        ))
        db.send_create_signal(u'wanglibao_fund', ['RedeemChargeRate'])

        # Adding field 'Fund.issuable'
        db.add_column(u'wanglibao_fund_fund', 'issuable',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Fund.redeemable'
        db.add_column(u'wanglibao_fund_fund', 'redeemable',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Fund.AIP_able'
        db.add_column(u'wanglibao_fund_fund', 'AIP_able',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'IssueChargeRate'
        db.delete_table(u'wanglibao_fund_issuechargerate')

        # Deleting model 'RedeemChargeRate'
        db.delete_table(u'wanglibao_fund_redeemchargerate')

        # Deleting field 'Fund.issuable'
        db.delete_column(u'wanglibao_fund_fund', 'issuable')

        # Deleting field 'Fund.redeemable'
        db.delete_column(u'wanglibao_fund_fund', 'redeemable')

        # Deleting field 'Fund.AIP_able'
        db.delete_column(u'wanglibao_fund_fund', 'AIP_able')


    models = {
        u'wanglibao_fund.fund': {
            'AIP_able': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'Meta': {'object_name': 'Fund'},
            'accumulated_face_value': ('django.db.models.fields.FloatField', [], {}),
            'brief': ('django.db.models.fields.TextField', [], {}),
            'buy_back_charge_rate': ('django.db.models.fields.TextField', [], {}),
            'buy_front_charge_rate': ('django.db.models.fields.TextField', [], {}),
            'earned_per_10k': ('django.db.models.fields.FloatField', [], {}),
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
            'profit_rate_7days': ('django.db.models.fields.FloatField', [], {}),
            'rate_day': ('django.db.models.fields.FloatField', [], {}),
            'redeemable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sale_back_charge_rate': ('django.db.models.fields.TextField', [], {}),
            'sale_front_charge_rate': ('django.db.models.fields.TextField', [], {}),
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
        u'wanglibao_fund.issuechargerate': {
            'Meta': {'object_name': 'IssueChargeRate'},
            'bottom_line': ('django.db.models.fields.FloatField', [], {}),
            'fund': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_fund.Fund']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'top_line': ('django.db.models.fields.FloatField', [], {}),
            'value': ('django.db.models.fields.FloatField', [], {}),
            'value_type': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        u'wanglibao_fund.redeemchargerate': {
            'Meta': {'object_name': 'RedeemChargeRate'},
            'bottom_line': ('django.db.models.fields.FloatField', [], {}),
            'fund': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_fund.Fund']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'top_line': ('django.db.models.fields.FloatField', [], {}),
            'value': ('django.db.models.fields.FloatField', [], {}),
            'value_type': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        }
    }

    complete_apps = ['wanglibao_fund']