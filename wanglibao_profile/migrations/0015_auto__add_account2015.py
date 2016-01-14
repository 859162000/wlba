# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Account2015'
        db.create_table(u'wanglibao_profile_account2015', (
            ('user_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('zc_ranking', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('tz_times', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('tz_amount', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=2)),
            ('tz_ranking_percent', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=2)),
            ('tz_max_amount', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=2)),
            ('tz_max_ranking_percent', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=2)),
            ('tz_sterm_amount', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=2)),
            ('tz_mterm_amount', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=2)),
            ('tz_lterm_amount', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=2)),
            ('income_total', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=2)),
            ('income_reward', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=2)),
            ('income_hb_expire', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=2)),
            ('income_jxq_expire', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=2)),
            ('invite_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('invite_income', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=2)),
        ))
        db.send_create_signal(u'wanglibao_profile', ['Account2015'])


    def backwards(self, orm):
        # Deleting model 'Account2015'
        db.delete_table(u'wanglibao_profile_account2015')


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
        u'wanglibao_profile.account2015': {
            'Meta': {'object_name': 'Account2015'},
            'income_hb_expire': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'}),
            'income_jxq_expire': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'}),
            'income_reward': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'}),
            'income_total': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'}),
            'invite_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'invite_income': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'}),
            'tz_amount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'}),
            'tz_lterm_amount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'}),
            'tz_max_amount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'}),
            'tz_max_ranking_percent': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'}),
            'tz_mterm_amount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'}),
            'tz_ranking_percent': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'}),
            'tz_sterm_amount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'}),
            'tz_times': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'zc_ranking': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'wanglibao_profile.wanglibaouserprofile': {
            'Meta': {'object_name': 'WanglibaoUserProfile'},
            'deposit_default_bank_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'first_bind_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'frozen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'gesture_is_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'gesture_pwd': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '9', 'blank': 'True'}),
            'id_is_valid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id_number': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'blank': 'True'}),
            'id_valid_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'investment_asset': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'investment_period': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'nick_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'phone_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'risk_level': ('django.db.models.fields.PositiveIntegerField', [], {'default': '2'}),
            'shumi_access_token': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'shumi_access_token_secret': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'shumi_request_token': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'shumi_request_token_secret': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'trade_pwd': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'trade_pwd_failed_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'trade_pwd_last_failed_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'utype': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '10'})
        }
    }

    complete_apps = ['wanglibao_profile']