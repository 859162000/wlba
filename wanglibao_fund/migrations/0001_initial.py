# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FundIssuer'
        db.create_table(u'wanglibao_fund_fundissuer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('home_page', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'wanglibao_fund', ['FundIssuer'])

        # Adding model 'Fund'
        db.create_table(u'wanglibao_fund_fund', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('product_code', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('issuer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_fund.FundIssuer'])),
            ('brief', self.gf('django.db.models.fields.TextField')()),
            ('face_value', self.gf('django.db.models.fields.FloatField')()),
            ('accumulated_face_value', self.gf('django.db.models.fields.FloatField')()),
            ('rate_day', self.gf('django.db.models.fields.FloatField')()),
            ('earned_per_10k', self.gf('django.db.models.fields.FloatField')()),
            ('profit_rate_7days', self.gf('django.db.models.fields.FloatField')()),
            ('profit_per_month', self.gf('django.db.models.fields.FloatField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('fund_date', self.gf('django.db.models.fields.DateField')()),
            ('sales_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('mode', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('scale', self.gf('django.db.models.fields.FloatField')()),
            ('hosted_bank', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('hosted_bank_description', self.gf('django.db.models.fields.TextField')()),
            ('performance_compare_baseline', self.gf('django.db.models.fields.TextField')()),
            ('invest_target', self.gf('django.db.models.fields.TextField')()),
            ('invest_scope', self.gf('django.db.models.fields.TextField')()),
            ('manager', self.gf('django.db.models.fields.TextField')()),
            ('portfolio', self.gf('django.db.models.fields.TextField')()),
            ('management_charge_rate', self.gf('django.db.models.fields.FloatField')()),
            ('frontend_hosting_charge_rate', self.gf('django.db.models.fields.FloatField')()),
            ('buy_front_charge_rate', self.gf('django.db.models.fields.TextField')()),
            ('buy_back_charge_rate', self.gf('django.db.models.fields.TextField')()),
            ('sale_front_charge_rate', self.gf('django.db.models.fields.TextField')()),
            ('sale_back_charge_rate', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'wanglibao_fund', ['Fund'])


    def backwards(self, orm):
        # Deleting model 'FundIssuer'
        db.delete_table(u'wanglibao_fund_fundissuer')

        # Deleting model 'Fund'
        db.delete_table(u'wanglibao_fund_fund')


    models = {
        u'wanglibao_fund.fund': {
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
        }
    }

    complete_apps = ['wanglibao_fund']