# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CashIssuer'
        db.create_table(u'wanglibao_cash_cashissuer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('home_page', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'wanglibao_cash', ['CashIssuer'])

        # Adding model 'Cash'
        db.create_table(u'wanglibao_cash_cash', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('issuer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_cash.CashIssuer'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('period', self.gf('django.db.models.fields.IntegerField')()),
            ('profit_rate_7days', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('profit_10000', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('how_to_buy', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('brief', self.gf('django.db.models.fields.TextField')()),
            ('buy_brief', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('redeem_brief', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('profit_brief', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('safe_brief', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'wanglibao_cash', ['Cash'])


    def backwards(self, orm):
        # Deleting model 'CashIssuer'
        db.delete_table(u'wanglibao_cash_cashissuer')

        # Deleting model 'Cash'
        db.delete_table(u'wanglibao_cash_cash')


    models = {
        u'wanglibao_cash.cash': {
            'Meta': {'object_name': 'Cash'},
            'brief': ('django.db.models.fields.TextField', [], {}),
            'buy_brief': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'how_to_buy': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issuer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_cash.CashIssuer']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'period': ('django.db.models.fields.IntegerField', [], {}),
            'profit_10000': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'profit_brief': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'profit_rate_7days': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'redeem_brief': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'safe_brief': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        u'wanglibao_cash.cashissuer': {
            'Meta': {'object_name': 'CashIssuer'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'home_page': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['wanglibao_cash']