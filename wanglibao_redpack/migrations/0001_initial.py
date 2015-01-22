# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Rule'
        db.create_table(u'wanglibao_redpack_rule', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('rtype', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('value', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('extra', self.gf('django.db.models.fields.CharField')(default='', max_length=30)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'wanglibao_redpack', ['Rule'])

        # Adding model 'RedPackEvent'
        db.create_table(u'wanglibao_redpack_redpackevent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('rule', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_redpack.Rule'])),
            ('describe', self.gf('django.db.models.fields.CharField')(default='', max_length=20)),
            ('give_mode', self.gf('django.db.models.fields.CharField')(default='', max_length=20, db_index=True)),
            ('give_start_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('give_end_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('available_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('unavailable_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('change_end_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('extra', self.gf('django.db.models.fields.CharField')(default='', max_length=20)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'wanglibao_redpack', ['RedPackEvent'])

        # Adding model 'RedPack'
        db.create_table(u'wanglibao_redpack_redpack', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_redpack.RedPackEvent'])),
            ('token', self.gf('django.db.models.fields.CharField')(default='', max_length=20, db_index=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='unused', max_length=20)),
        ))
        db.send_create_signal(u'wanglibao_redpack', ['RedPack'])

        # Adding model 'RedPackRecord'
        db.create_table(u'wanglibao_redpack_redpackrecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('redpack', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_redpack.RedPack'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('rule', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_redpack.Rule'])),
            ('change_platform', self.gf('django.db.models.fields.CharField')(default='pc', max_length=20)),
            ('apply_platform', self.gf('django.db.models.fields.CharField')(default='pc', max_length=20)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('apply_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('order_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('available', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'wanglibao_redpack', ['RedPackRecord'])


    def backwards(self, orm):
        # Deleting model 'Rule'
        db.delete_table(u'wanglibao_redpack_rule')

        # Deleting model 'RedPackEvent'
        db.delete_table(u'wanglibao_redpack_redpackevent')

        # Deleting model 'RedPack'
        db.delete_table(u'wanglibao_redpack_redpack')

        # Deleting model 'RedPackRecord'
        db.delete_table(u'wanglibao_redpack_redpackrecord')


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
        u'wanglibao_redpack.redpack': {
            'Meta': {'object_name': 'RedPack'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_redpack.RedPackEvent']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'unused'", 'max_length': '20'}),
            'token': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'db_index': 'True'})
        },
        u'wanglibao_redpack.redpackevent': {
            'Meta': {'object_name': 'RedPackEvent'},
            'available_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'change_end_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'describe': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'extra': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'give_end_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'give_mode': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'db_index': 'True'}),
            'give_start_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'rule': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_redpack.Rule']"}),
            'unavailable_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'wanglibao_redpack.redpackrecord': {
            'Meta': {'object_name': 'RedPackRecord'},
            'apply_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'apply_platform': ('django.db.models.fields.CharField', [], {'default': "'pc'", 'max_length': '20'}),
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'change_platform': ('django.db.models.fields.CharField', [], {'default': "'pc'", 'max_length': '20'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'redpack': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_redpack.RedPack']"}),
            'rule': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_redpack.Rule']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'wanglibao_redpack.rule': {
            'Meta': {'object_name': 'Rule'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'extra': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'rtype': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['wanglibao_redpack']