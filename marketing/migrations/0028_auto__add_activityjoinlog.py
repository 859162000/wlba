# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ActivityJoinLog'
        db.create_table(u'marketing_activityjoinlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('action_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('action_message', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('join_times', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=6)),
            ('gift_name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'marketing', ['ActivityJoinLog'])


    def backwards(self, orm):
        # Deleting model 'ActivityJoinLog'
        db.delete_table(u'marketing_activityjoinlog')


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
        u'marketing.activityjoinlog': {
            'Meta': {'object_name': 'ActivityJoinLog'},
            'action_message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'action_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'gift_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'join_times': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '6'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
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
        u'marketing.channels': {
            'Meta': {'object_name': 'Channels'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '12', 'db_index': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'})
        },
        u'marketing.clientdata': {
            'Meta': {'ordering': "['-create_time']", 'object_name': 'ClientData'},
            'action': ('django.db.models.fields.IntegerField', [], {'max_length': '2'}),
            'channelid': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'userdevice': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'marketing.introducedby': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'IntroducedBy'},
            'bought_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['marketing.Channels']", 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'creator'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'gift_send_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'introduced_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'introduces'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'product_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'marketing.introducedbyreward': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'IntroducedByReward'},
            'activity_amount_min': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'activity_end_at': ('django.db.models.fields.DateTimeField', [], {}),
            'activity_start_at': ('django.db.models.fields.DateTimeField', [], {}),
            'checked_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'checked_status': ('django.db.models.fields.IntegerField', [], {'max_length': '2'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'first_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'first_bought_at': ('django.db.models.fields.DateTimeField', [], {}),
            'first_reward': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'introduced_by_person': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'introduced_person'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'introduced_reward': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'introduced_send_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'introduced_send_status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'percent_reward': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['wanglibao_p2p.P2PProduct']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'user_send_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'user_send_status': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'marketing.invitecode': {
            'Meta': {'ordering': "['id']", 'object_name': 'InviteCode'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '6', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_used': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'marketing.newsandreport': {
            'Meta': {'ordering': "['-score']", 'object_name': 'NewsAndReport'},
            'content': ('ckeditor.fields.RichTextField', [], {'default': "''", 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True'}),
            'hits': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'marketing.playlist': {
            'Meta': {'object_name': 'PlayList'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'amount_max': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'amount_min': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'checked_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '2'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.IntegerField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'play_at': ('django.db.models.fields.DateTimeField', [], {}),
            'ranking': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'redpackevent': ('django.db.models.fields.TextField', [], {}),
            'reward': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'start': ('django.db.models.fields.IntegerField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'marketing.promotiontoken': {
            'Meta': {'object_name': 'PromotionToken'},
            'token': ('django.db.models.fields.CharField', [], {'default': "'Cd276qLyQsuu72U4-xBJVA'", 'max_length': '64', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'marketing.reward': {
            'Meta': {'ordering': "['-create_time']", 'object_name': 'Reward'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_used': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'marketing.rewardrecord': {
            'Meta': {'ordering': "['-create_time']", 'object_name': 'RewardRecord'},
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reward': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['marketing.Reward']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'marketing.sitedata': {
            'Meta': {'object_name': 'SiteData'},
            'demand_deposit_interest_rate': ('django.db.models.fields.FloatField', [], {'default': '0.35'}),
            'earning_rate': ('django.db.models.fields.CharField', [], {'default': "u'10%-15%'", 'max_length': '16'}),
            'highest_earning_rate': ('django.db.models.fields.FloatField', [], {'default': '15'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invest_threshold': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'one_year_interest_rate': ('django.db.models.fields.FloatField', [], {'default': '3'}),
            'p2p_total_earning': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'p2p_total_trade': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'product_release_time': ('django.db.models.fields.CharField', [], {'default': "u'17:30'", 'max_length': '128'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'marketing.timelysitedata': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'TimelySiteData'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'freeze_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'p2p_margin': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'total_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'user_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
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
            'end_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 7, 6, 0, 0)'}),
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
        }
    }

    complete_apps = ['marketing']