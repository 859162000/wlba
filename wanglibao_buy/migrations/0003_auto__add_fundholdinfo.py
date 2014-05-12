# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FundHoldInfo'
        db.create_table(u'wanglibao_buy_fundholdinfo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('trade_account', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('fund_code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('fund_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('share_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('current_remain_share', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('usable_remain_share', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('freeze_remain_share', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('melon_method', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('t_freeze_remain_share', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('expire_shares', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('unpaid_income', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('pernet_value', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('market_value', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=3)),
            ('nav_date', self.gf('django.db.models.fields.DateField')()),
            ('bank_account', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('bank_name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('bank_serial', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('fund_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('fund_type_to_cn', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('rapid_redeem', self.gf('django.db.models.fields.BooleanField')()),
            ('capital_mode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('create_date', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'wanglibao_buy', ['FundHoldInfo'])


    def backwards(self, orm):
        # Deleting model 'FundHoldInfo'
        db.delete_table(u'wanglibao_buy_fundholdinfo')


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
        }
    }

    complete_apps = ['wanglibao_buy']