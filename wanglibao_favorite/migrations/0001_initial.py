# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FavoriteTrust'
        db.create_table(u'wanglibao_favorite_favoritetrust', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trust.Trust'])),
        ))
        db.send_create_signal(u'wanglibao_favorite', ['FavoriteTrust'])

        # Adding model 'FavoriteFinancing'
        db.create_table(u'wanglibao_favorite_favoritefinancing', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_bank_financing.BankFinancing'])),
        ))
        db.send_create_signal(u'wanglibao_favorite', ['FavoriteFinancing'])

        # Adding model 'FavoriteFund'
        db.create_table(u'wanglibao_favorite_favoritefund', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_fund.Fund'])),
        ))
        db.send_create_signal(u'wanglibao_favorite', ['FavoriteFund'])


    def backwards(self, orm):
        # Deleting model 'FavoriteTrust'
        db.delete_table(u'wanglibao_favorite_favoritetrust')

        # Deleting model 'FavoriteFinancing'
        db.delete_table(u'wanglibao_favorite_favoritefinancing')

        # Deleting model 'FavoriteFund'
        db.delete_table(u'wanglibao_favorite_favoritefund')


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
            'brief': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
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
        u'wanglibao_favorite.favoritefinancing': {
            'Meta': {'object_name': 'FavoriteFinancing'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_bank_financing.BankFinancing']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'wanglibao_favorite.favoritefund': {
            'Meta': {'object_name': 'FavoriteFund'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_fund.Fund']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'wanglibao_favorite.favoritetrust': {
            'Meta': {'object_name': 'FavoriteTrust'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['trust.Trust']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
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
        }
    }

    complete_apps = ['wanglibao_favorite']