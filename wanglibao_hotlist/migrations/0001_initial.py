# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'HotTrust'
        db.create_table(u'wanglibao_hotlist_hottrust', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('trust', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['trust.Trust'], unique=True)),
            ('hot_score', self.gf('django.db.models.fields.IntegerField')()),
            ('added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 3, 3, 10, 23, 58), null=True)),
        ))
        db.send_create_signal(u'wanglibao_hotlist', ['HotTrust'])

        # Adding model 'HotFinancing'
        db.create_table(u'wanglibao_hotlist_hotfinancing', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bank_financing', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['wanglibao_bank_financing.BankFinancing'], unique=True)),
            ('hot_score', self.gf('django.db.models.fields.IntegerField')()),
            ('added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 3, 3, 10, 23, 58), null=True)),
        ))
        db.send_create_signal(u'wanglibao_hotlist', ['HotFinancing'])

        # Adding model 'HotFund'
        db.create_table(u'wanglibao_hotlist_hotfund', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('Fund', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['wanglibao_fund.Fund'], unique=True)),
            ('hot_score', self.gf('django.db.models.fields.IntegerField')()),
            ('added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 3, 3, 10, 23, 58), null=True)),
        ))
        db.send_create_signal(u'wanglibao_hotlist', ['HotFund'])


    def backwards(self, orm):
        # Deleting model 'HotTrust'
        db.delete_table(u'wanglibao_hotlist_hottrust')

        # Deleting model 'HotFinancing'
        db.delete_table(u'wanglibao_hotlist_hotfinancing')

        # Deleting model 'HotFund'
        db.delete_table(u'wanglibao_hotlist_hotfund')


    models = {
        u'trust.issuer': {
            'Meta': {'object_name': 'Issuer'},
            'appear_on_market': ('django.db.models.fields.BooleanField', [], {}),
            'business_range': ('django.db.models.fields.TextField', [], {}),
            'chairman_of_board': ('django.db.models.fields.TextField', [], {}),
            'english_name': ('django.db.models.fields.TextField', [], {}),
            'founded_at': ('django.db.models.fields.DateField', [], {}),
            'geo_region': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'legal_presentative': ('django.db.models.fields.TextField', [], {}),
            'major_stockholder': ('django.db.models.fields.TextField', [], {}),
            'manager': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'note': ('django.db.models.fields.TextField', [], {}),
            'registered_capital': ('django.db.models.fields.IntegerField', [], {}),
            'shareholder_background': ('django.db.models.fields.TextField', [], {}),
            'shareholders': ('django.db.models.fields.TextField', [], {}),
            'short_name': ('django.db.models.fields.TextField', [], {})
        },
        u'trust.trust': {
            'Meta': {'object_name': 'Trust'},
            'available_region': ('django.db.models.fields.TextField', [], {}),
            'brief': ('django.db.models.fields.TextField', [], {}),
            'earning_description': ('django.db.models.fields.TextField', [], {}),
            'expected_earning_rate': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investment_threshold': ('django.db.models.fields.FloatField', [], {}),
            'issue_date': ('django.db.models.fields.DateField', [], {}),
            'issuer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['trust.Issuer']"}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'note': ('django.db.models.fields.TextField', [], {}),
            'payment': ('django.db.models.fields.TextField', [], {}),
            'period': ('django.db.models.fields.FloatField', [], {}),
            'product_name': ('django.db.models.fields.TextField', [], {}),
            'related_info': ('django.db.models.fields.TextField', [], {}),
            'risk_management': ('django.db.models.fields.TextField', [], {}),
            'scale': ('django.db.models.fields.IntegerField', [], {}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'type': ('django.db.models.fields.TextField', [], {}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'usage_description': ('django.db.models.fields.TextField', [], {})
        },
        u'wanglibao_bank_financing.bank': {
            'Meta': {'object_name': 'Bank'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'home_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'wanglibao_bank_financing.bankfinancing': {
            'Meta': {'object_name': 'BankFinancing'},
            'bank': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_bank_financing.Bank']"}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'face_value': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invest_method': ('django.db.models.fields.TextField', [], {}),
            'invest_step': ('django.db.models.fields.FloatField', [], {}),
            'invest_target': ('django.db.models.fields.TextField', [], {}),
            'invest_threshold': ('django.db.models.fields.FloatField', [], {}),
            'max_expected_profit_rate': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'period': ('django.db.models.fields.FloatField', [], {}),
            'principle_guaranteed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'product_code': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'product_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'profit_calculation': ('django.db.models.fields.TextField', [], {}),
            'profit_end_date': ('django.db.models.fields.DateField', [], {}),
            'profit_rate': ('django.db.models.fields.FloatField', [], {}),
            'profit_start_date': ('django.db.models.fields.DateField', [], {}),
            'profit_target': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'profit_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'region': ('django.db.models.fields.TextField', [], {}),
            'related_target': ('django.db.models.fields.TextField', [], {}),
            'risk_level': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'sale_end_date': ('django.db.models.fields.DateField', [], {}),
            'sale_start_date': ('django.db.models.fields.DateField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'\\u5728\\u552e'", 'max_length': '8'})
        },
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
        u'wanglibao_hotlist.hotfinancing': {
            'Meta': {'ordering': "['-added']", 'object_name': 'HotFinancing'},
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 3, 10, 23, 58)', 'null': 'True'}),
            'bank_financing': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['wanglibao_bank_financing.BankFinancing']", 'unique': 'True'}),
            'hot_score': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'wanglibao_hotlist.hotfund': {
            'Fund': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['wanglibao_fund.Fund']", 'unique': 'True'}),
            'Meta': {'ordering': "['-added']", 'object_name': 'HotFund'},
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 3, 10, 23, 58)', 'null': 'True'}),
            'hot_score': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'wanglibao_hotlist.hottrust': {
            'Meta': {'ordering': "['-added']", 'object_name': 'HotTrust'},
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 3, 10, 23, 58)', 'null': 'True'}),
            'hot_score': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'trust': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['trust.Trust']", 'unique': 'True'})
        }
    }

    complete_apps = ['wanglibao_hotlist']