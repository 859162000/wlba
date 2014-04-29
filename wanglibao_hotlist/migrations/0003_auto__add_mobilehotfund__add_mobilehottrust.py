# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MobileHotFund'
        db.create_table(u'wanglibao_hotlist_mobilehotfund', (
            (u'hotfund_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['wanglibao_hotlist.HotFund'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'wanglibao_hotlist', ['MobileHotFund'])

        # Adding model 'MobileHotTrust'
        db.create_table(u'wanglibao_hotlist_mobilehottrust', (
            (u'hottrust_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['wanglibao_hotlist.HotTrust'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'wanglibao_hotlist', ['MobileHotTrust'])


    def backwards(self, orm):
        # Deleting model 'MobileHotFund'
        db.delete_table(u'wanglibao_hotlist_mobilehotfund')

        # Deleting model 'MobileHotTrust'
        db.delete_table(u'wanglibao_hotlist_mobilehottrust')


    models = {
        u'trust.issuer': {
            'Meta': {'object_name': 'Issuer'},
            'appear_on_market': ('django.db.models.fields.BooleanField', [], {}),
            'business_range': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'chairman_of_board': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'english_name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'founded_at': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'geo_region': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'legal_presentative': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'major_stockholder': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'manager': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'registered_capital': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'shareholder_background': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'shareholders': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.TextField', [], {})
        },
        u'trust.trust': {
            'Meta': {'object_name': 'Trust'},
            'available_region': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'brief': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'consignee': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'earning_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'expected_earning_rate': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investment_threshold': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'issue_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'issuer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['trust.Issuer']"}),
            'mortgage': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'mortgage_rate': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'payment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'period': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'product_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'related_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'risk_management': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'scale': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'\\u5728\\u552e'", 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'usage_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'wanglibao_bank_financing.bank': {
            'Meta': {'object_name': 'Bank'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'home_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'wanglibao_bank_financing.bankfinancing': {
            'Meta': {'object_name': 'BankFinancing'},
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'bank': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_bank_financing.Bank']"}),
            'bank_pre_redeem_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'bank_pre_redeemable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'brief': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'buy_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'client_redeemable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "u'\\u4eba\\u6c11\\u5e01'", 'max_length': '32'}),
            'expected_rate': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investment_step': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'investment_threshold': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'investment_type': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'issue_end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'issue_start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'issue_target': ('django.db.models.fields.CharField', [], {'default': "u'\\u4e2a\\u4eba'", 'max_length': '16'}),
            'liquidity_level': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'max_expected_profit_rate': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'max_profit_rate': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'period': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'pledgable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'principle_guaranteed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'profit_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'profit_end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'profit_start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'profit_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'rate_compare_to_saving': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'redeem_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'region': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'risk_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'risk_level': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'\\u5728\\u552e'", 'max_length': '8'})
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
        u'wanglibao_hotlist.hotfinancing': {
            'Meta': {'ordering': "['-hot_score']", 'object_name': 'HotFinancing'},
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'bank_financing': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['wanglibao_bank_financing.BankFinancing']", 'unique': 'True'}),
            'hot_score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'wanglibao_hotlist.hotfund': {
            'Meta': {'ordering': "['-hot_score']", 'object_name': 'HotFund'},
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'fund': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['wanglibao_fund.Fund']", 'unique': 'True'}),
            'hot_score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'wanglibao_hotlist.hottrust': {
            'Meta': {'ordering': "['-hot_score']", 'object_name': 'HotTrust'},
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'hot_score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'trust': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['trust.Trust']", 'unique': 'True'})
        },
        u'wanglibao_hotlist.mobilehotfund': {
            'Meta': {'ordering': "['-hot_score']", 'object_name': 'MobileHotFund', '_ormbases': [u'wanglibao_hotlist.HotFund']},
            u'hotfund_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['wanglibao_hotlist.HotFund']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'wanglibao_hotlist.mobilehottrust': {
            'Meta': {'ordering': "['-hot_score']", 'object_name': 'MobileHotTrust', '_ormbases': [u'wanglibao_hotlist.HotTrust']},
            u'hottrust_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['wanglibao_hotlist.HotTrust']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['wanglibao_hotlist']