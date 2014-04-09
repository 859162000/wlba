# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Cash.buy_url'
        db.alter_column(u'wanglibao_cash_cash', 'buy_url', self.gf('django.db.models.fields.URLField')(max_length=1024))

    def backwards(self, orm):

        # Changing field 'Cash.buy_url'
        db.alter_column(u'wanglibao_cash_cash', 'buy_url', self.gf('django.db.models.fields.URLField')(max_length=200))

    models = {
        u'wanglibao_cash.cash': {
            'Meta': {'object_name': 'Cash'},
            'brief': ('django.db.models.fields.TextField', [], {}),
            'buy_brief': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'buy_text': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'buy_url': ('django.db.models.fields.URLField', [], {'max_length': '1024'}),
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