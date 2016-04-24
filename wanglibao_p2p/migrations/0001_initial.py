# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'P2PProduct'
        db.create_table(u'wanglibao_p2p_p2pproduct', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('category', self.gf('django.db.models.fields.CharField')(default=u'\u666e\u901a', max_length=16)),
            ('types', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('serial_number', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default=u'\u5f55\u6807', max_length=16, db_index=True)),
            ('period', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('brief', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('expected_earning_rate', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('excess_earning_rate', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('excess_earning_description', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('pay_method', self.gf('django.db.models.fields.CharField')(default=u'\u7b49\u989d\u672c\u606f', max_length=32)),
            ('amortization_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('repaying_source', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('total_amount', self.gf('django.db.models.fields.BigIntegerField')(default=1)),
            ('ordered_amount', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('publish_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2016, 5, 4, 0, 0), db_index=True)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2016, 5, 14, 0, 0))),
            ('soldout_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('make_loans_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('limit_per_user', self.gf('django.db.models.fields.FloatField')(default=1)),
            ('warrant_company', self.gf('django.db.models.fields.CharField')(max_length=64, null=True)),
            ('flow_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2016, 4, 24, 0, 0), null=True, db_index=True, blank=True)),
            ('sync_id', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal(u'wanglibao_p2p', ['P2PProduct'])

        # Adding model 'P2PEquity'
        db.create_table(u'wanglibao_p2p_p2pequity', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='equities', to=orm['auth.User'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='equities', to=orm['wanglibao_p2p.P2PProduct'])),
            ('equity', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('confirm', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('confirm_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('sync_id', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal(u'wanglibao_p2p', ['P2PEquity'])

        # Adding unique constraint on 'P2PEquity', fields ['user', 'product']
        db.create_unique(u'wanglibao_p2p_p2pequity', ['user_id', 'product_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'P2PEquity', fields ['user', 'product']
        db.delete_unique(u'wanglibao_p2p_p2pequity', ['user_id', 'product_id'])

        # Deleting model 'P2PProduct'
        db.delete_table(u'wanglibao_p2p_p2pproduct')

        # Deleting model 'P2PEquity'
        db.delete_table(u'wanglibao_p2p_p2pequity')


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
        u'wanglibao_p2p.p2pequity': {
            'Meta': {'ordering': "('-created_at',)", 'unique_together': "(('user', 'product'),)", 'object_name': 'P2PEquity'},
            'confirm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'confirm_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'equity': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'equities'", 'to': u"orm['wanglibao_p2p.P2PProduct']"}),
            'sync_id': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'equities'", 'to': u"orm['auth.User']"})
        },
        u'wanglibao_p2p.p2pproduct': {
            'Meta': {'object_name': 'P2PProduct'},
            'amortization_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'brief': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'default': "u'\\u666e\\u901a'", 'max_length': '16'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2016, 5, 14, 0, 0)'}),
            'excess_earning_description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'excess_earning_rate': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'expected_earning_rate': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'flow_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2016, 4, 24, 0, 0)', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit_per_user': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'make_loans_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ordered_amount': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'pay_method': ('django.db.models.fields.CharField', [], {'default': "u'\\u7b49\\u989d\\u672c\\u606f'", 'max_length': '32'}),
            'period': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'publish_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2016, 5, 4, 0, 0)', 'db_index': 'True'}),
            'repaying_source': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'serial_number': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'soldout_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'\\u5f55\\u6807'", 'max_length': '16', 'db_index': 'True'}),
            'sync_id': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'total_amount': ('django.db.models.fields.BigIntegerField', [], {'default': '1'}),
            'types': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'warrant_company': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'})
        }
    }

    complete_apps = ['wanglibao_p2p']