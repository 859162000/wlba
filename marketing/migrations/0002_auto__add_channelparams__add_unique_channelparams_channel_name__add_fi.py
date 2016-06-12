# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ChannelParams'
        db.create_table(u'marketing_channelparams', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(related_name='all_params', to=orm['marketing.Channels'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('internal_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('external_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('default_value', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('get_from', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('level', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=2)),
            ('parent', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('quote_url_decrypt', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_decrypt', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('decrypt_method', self.gf('django.db.models.fields.CharField')(default=None, max_length=30, null=True, blank=True)),
            ('is_save_session', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_join_sign', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True)),
            ('is_abandoned', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'marketing', ['ChannelParams'])

        # Adding unique constraint on 'ChannelParams', fields ['channel', 'name']
        db.create_unique(u'marketing_channelparams', ['channel_id', 'name'])

        # Adding field 'Channels.coop_callback'
        db.add_column(u'marketing_channels', 'coop_callback',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Channels.disable_csrf'
        db.add_column(u'marketing_channels', 'disable_csrf',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Channels.sign_format'
        db.add_column(u'marketing_channels', 'sign_format',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Channels.coop_charge_name'
        db.add_column(u'marketing_channels', 'coop_charge_name',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Channels.coop_charge_phone'
        db.add_column(u'marketing_channels', 'coop_charge_phone',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Removing unique constraint on 'ChannelParams', fields ['channel', 'name']
        db.delete_unique(u'marketing_channelparams', ['channel_id', 'name'])

        # Deleting model 'ChannelParams'
        db.delete_table(u'marketing_channelparams')

        # Deleting field 'Channels.coop_callback'
        db.delete_column(u'marketing_channels', 'coop_callback')

        # Deleting field 'Channels.disable_csrf'
        db.delete_column(u'marketing_channels', 'disable_csrf')

        # Deleting field 'Channels.sign_format'
        db.delete_column(u'marketing_channels', 'sign_format')

        # Deleting field 'Channels.coop_charge_name'
        db.delete_column(u'marketing_channels', 'coop_charge_name')

        # Deleting field 'Channels.coop_charge_phone'
        db.delete_column(u'marketing_channels', 'coop_charge_phone')


    models = {
        u'marketing.channelparams': {
            'Meta': {'unique_together': "(('channel', 'name'),)", 'object_name': 'ChannelParams'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'all_params'", 'to': u"orm['marketing.Channels']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'decrypt_method': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'default_value': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'external_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'get_from': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'is_abandoned': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'is_decrypt': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_join_sign': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_save_session': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'level': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '2'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'parent': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'quote_url_decrypt': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'marketing.channels': {
            'Meta': {'object_name': 'Channels'},
            'classification': ('django.db.models.fields.CharField', [], {'default': "'----'", 'max_length': '20'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '12', 'db_index': 'True'}),
            'coop_callback': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'coop_charge_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'coop_charge_phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'coop_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '2'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'disable_csrf': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'is_abandoned': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'merge_code': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'platform': ('django.db.models.fields.CharField', [], {'default': "'full'", 'max_length': '20'}),
            'sign_format': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'start_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['marketing']