# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'RedPackEvent.auto_extension'
        db.add_column(u'wanglibao_redpack_redpackevent', 'auto_extension',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'RedPackEvent.auto_extension_days'
        db.add_column(u'wanglibao_redpack_redpackevent', 'auto_extension_days',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'RedPackEvent.auto_extension'
        db.delete_column(u'wanglibao_redpack_redpackevent', 'auto_extension')

        # Deleting field 'RedPackEvent.auto_extension_days'
        db.delete_column(u'wanglibao_redpack_redpackevent', 'auto_extension_days')


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
        u'marketing.activity': {
            'Meta': {'ordering': "['-create_time']", 'object_name': 'Activity'},
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'rule': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['marketing.ActivityRule']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'marketing.activityrule': {
            'Meta': {'ordering': "['-create_time']", 'object_name': 'ActivityRule'},
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'rule_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '4'}),
            'rule_type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'wanglibao_p2p.contracttemplate': {
            'Meta': {'object_name': 'ContractTemplate'},
            'content': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'content_preview': ('django.db.models.fields.TextField', [], {'default': "''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'wanglibao_p2p.p2pproduct': {
            'Meta': {'object_name': 'P2PProduct'},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['marketing.Activity']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'amortization_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'baoli_original_contract_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'baoli_original_contract_number': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'baoli_trade_relation': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'borrower_address': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'borrower_bankcard': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'borrower_bankcard_bank_branch': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'borrower_bankcard_bank_city': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'borrower_bankcard_bank_code': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'borrower_bankcard_bank_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'borrower_bankcard_bank_province': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'borrower_bankcard_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'borrower_id_number': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'borrower_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'borrower_phone': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'bought_amount': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'bought_amount_random': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'bought_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'bought_count_random': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'bought_people_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'brief': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'default': "u'\\u666e\\u901a'", 'max_length': '16'}),
            'contract_serial_number': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'contract_template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.ContractTemplate']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 8, 27, 0, 0)'}),
            'excess_earning_description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'excess_earning_rate': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'expected_earning_rate': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'extra_data': ('wanglibao.fields.JSONFieldUtf8', [], {'blank': 'True'}),
            'hide': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit_per_user': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'make_loans_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ordered_amount': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'pay_method': ('django.db.models.fields.CharField', [], {'default': "u'\\u7b49\\u989d\\u672c\\u606f'", 'max_length': '32'}),
            'period': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'publish_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'repaying_source': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'serial_number': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True', 'null': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'short_usage': ('django.db.models.fields.TextField', [], {}),
            'soldout_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'\\u5f55\\u6807'", 'max_length': '16'}),
            'total_amount': ('django.db.models.fields.BigIntegerField', [], {'default': '1'}),
            'usage': ('django.db.models.fields.TextField', [], {}),
            'version': ('concurrency.fields.IntegerVersionField', [], {'name': "'version'", 'db_tablespace': "''"}),
            'warrant_company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.WarrantCompany']"})
        },
        u'wanglibao_p2p.warrantcompany': {
            'Meta': {'object_name': 'WarrantCompany'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'wanglibao_redpack.income': {
            'Meta': {'object_name': 'Income'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '20', 'decimal_places': '2'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'earning': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '20', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invite': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invite'", 'to': u"orm['auth.User']"}),
            'level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'order_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.P2PProduct']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user'", 'to': u"orm['auth.User']"})
        },
        u'wanglibao_redpack.interesthike': {
            'Meta': {'object_name': 'InterestHike'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '20', 'decimal_places': '2'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro_total': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'invalid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.P2PProduct']"}),
            'rate': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '20', 'decimal_places': '5'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'wanglibao_redpack.redpack': {
            'Meta': {'object_name': 'RedPack'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_redpack.RedPackEvent']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'unused'", 'max_length': '20'}),
            'token': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'db_index': 'True'})
        },
        u'wanglibao_redpack.redpackevent': {
            'Meta': {'object_name': 'RedPackEvent'},
            'amount': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'apply_platform': ('django.db.models.fields.CharField', [], {'default': "'\\xe5\\x85\\xa8\\xe5\\xb9\\xb3\\xe5\\x8f\\xb0'", 'max_length': '10'}),
            'auto_extension': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'auto_extension_days': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'available_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'describe': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'give_end_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'give_mode': ('django.db.models.fields.CharField', [], {'default': "u'\\u6ce8\\u518c'", 'max_length': '20', 'db_index': 'True'}),
            'give_platform': ('django.db.models.fields.CharField', [], {'default': "'\\xe5\\x85\\xa8\\xe5\\xb9\\xb3\\xe5\\x8f\\xb0'", 'max_length': '10'}),
            'give_start_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'highest_amount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'invest_amount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'rtype': ('django.db.models.fields.CharField', [], {'default': "'\\xe7\\x9b\\xb4\\xe6\\x8a\\xb5\\xe7\\xba\\xa2\\xe5\\x8c\\x85'", 'max_length': '20'}),
            'target_channel': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'blank': 'True'}),
            'unavailable_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'wanglibao_redpack.redpackrecord': {
            'Meta': {'object_name': 'RedPackRecord'},
            'apply_amount': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True'}),
            'apply_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'apply_platform': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'change_platform': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_index': 'True'}),
            'redpack': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_redpack.RedPack']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['wanglibao_redpack']