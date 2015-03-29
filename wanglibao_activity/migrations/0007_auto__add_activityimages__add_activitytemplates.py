# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ActivityImages'
        db.create_table(u'wanglibao_activity_activityimages', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('img_type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('img', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('desc_one', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('desc_two', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')()),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'wanglibao_activity', ['ActivityImages'])

        # Adding model 'ActivityTemplates'
        db.create_table(u'wanglibao_activity_activitytemplates', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('logo_other', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('location', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('banner', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('is_activity_desc', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=20)),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('desc_time', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('is_reward', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=20)),
            ('reward_img', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('reward_desc', self.gf('ckeditor.fields.RichTextField')(null=True, blank=True)),
            ('is_introduce', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=20)),
            ('introduce_desc', self.gf('ckeditor.fields.RichTextField')(null=True, blank=True)),
            ('introduce_img', self.gf('ckeditor.fields.RichTextField')(null=True, blank=True)),
            ('is_teacher', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=20)),
            ('teacher_desc', self.gf('ckeditor.fields.RichTextField')(null=True, blank=True)),
            ('is_rule_use', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=20)),
            ('rule_use', self.gf('ckeditor.fields.RichTextField')(null=True, blank=True)),
            ('is_rule_activity', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=20)),
            ('rule_activity', self.gf('ckeditor.fields.RichTextField')(null=True, blank=True)),
            ('is_rule_reward', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=20)),
            ('rule_reward', self.gf('ckeditor.fields.RichTextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'wanglibao_activity', ['ActivityTemplates'])


    def backwards(self, orm):
        # Deleting model 'ActivityImages'
        db.delete_table(u'wanglibao_activity_activityimages')

        # Deleting model 'ActivityTemplates'
        db.delete_table(u'wanglibao_activity_activitytemplates')


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
        u'wanglibao_activity.activity': {
            'Meta': {'ordering': "['-priority']", 'object_name': 'Activity'},
            'banner': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'default': "u'\\u7ad9\\u5185\\u6d3b\\u52a8'", 'max_length': '20'}),
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_stopped': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'platform': ('django.db.models.fields.CharField', [], {'default': "u'\\u5168\\u5e73\\u53f0'", 'max_length': '20'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'product_cats': ('django.db.models.fields.CharField', [], {'default': "u'P2P\\u4ea7\\u54c1'", 'max_length': '20'}),
            'product_ids': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'start_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'stopped_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'template': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'wanglibao_activity.activityimages': {
            'Meta': {'object_name': 'ActivityImages'},
            'desc_one': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'desc_two': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'img_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'priority': ('django.db.models.fields.IntegerField', [], {})
        },
        u'wanglibao_activity.activityrecord': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'ActivityRecord'},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_activity.Activity']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'income': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'msg_type': ('django.db.models.fields.CharField', [], {'default': "u'\\u53ea\\u8bb0\\u5f55'", 'max_length': '20'}),
            'platform': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'rule': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_activity.ActivityRule']"}),
            'trigger_at': ('django.db.models.fields.DateTimeField', [], {}),
            'trigger_node': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'wanglibao_activity.activityrule': {
            'Meta': {'object_name': 'ActivityRule'},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_activity.Activity']"}),
            'both_share': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'gift_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'income': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'is_introduced': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_used': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_amount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'min_amount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'msg_template': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'msg_template_introduce': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'redpack': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'reward': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'rule_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'rule_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'send_type': ('django.db.models.fields.CharField', [], {'default': "u'\\u7cfb\\u7edf\\u5b9e\\u65f6\\u53d1\\u653e'", 'max_length': '20'}),
            'sms_template': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'sms_template_introduce': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'trigger_node': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'wanglibao_activity.activitytemplates': {
            'Meta': {'object_name': 'ActivityTemplates'},
            'banner': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'desc_time': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'introduce_desc': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'introduce_img': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'is_activity_desc': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '20'}),
            'is_introduce': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '20'}),
            'is_reward': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '20'}),
            'is_rule_activity': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '20'}),
            'is_rule_reward': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '20'}),
            'is_rule_use': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '20'}),
            'is_teacher': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '20'}),
            'location': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'logo_other': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'reward_desc': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'reward_img': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'rule_activity': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'rule_reward': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'rule_use': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'teacher_desc': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['wanglibao_activity']