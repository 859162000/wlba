# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'ActivityImages.desc_two'
        db.alter_column(u'wanglibao_activity_activityimages', 'desc_two', self.gf('django.db.models.fields.TextField')())

        # Changing field 'ActivityImages.desc_one'
        db.alter_column(u'wanglibao_activity_activityimages', 'desc_one', self.gf('django.db.models.fields.TextField')())
        # Deleting field 'ActivityTemplates.introduce_desc'
        db.delete_column(u'wanglibao_activity_activitytemplates', 'introduce_desc')

        # Adding field 'ActivityTemplates.is_login'
        db.add_column(u'wanglibao_activity_activitytemplates', 'is_login',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'ActivityTemplates.login_desc'
        db.add_column(u'wanglibao_activity_activitytemplates', 'login_desc',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True),
                      keep_default=False)

        # Adding field 'ActivityTemplates.desc_img'
        db.add_column(u'wanglibao_activity_activitytemplates', 'desc_img',
                      self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True),
                      keep_default=False)

        # Adding field 'ActivityTemplates.is_footer'
        db.add_column(u'wanglibao_activity_activitytemplates', 'is_footer',
                      self.gf('django.db.models.fields.IntegerField')(default=0, max_length=20),
                      keep_default=False)

        # Adding field 'ActivityTemplates.footer_color'
        db.add_column(u'wanglibao_activity_activitytemplates', 'footer_color',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'ActivityTemplates.is_earning_one'
        db.add_column(u'wanglibao_activity_activitytemplates', 'is_earning_one',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'ActivityTemplates.is_earning_two'
        db.add_column(u'wanglibao_activity_activitytemplates', 'is_earning_two',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'ActivityTemplates.is_earning_three'
        db.add_column(u'wanglibao_activity_activitytemplates', 'is_earning_three',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'ActivityTemplates.is_background'
        db.add_column(u'wanglibao_activity_activitytemplates', 'is_background',
                      self.gf('django.db.models.fields.IntegerField')(default=0, max_length=20),
                      keep_default=False)

        # Adding field 'ActivityTemplates.background_img'
        db.add_column(u'wanglibao_activity_activitytemplates', 'background_img',
                      self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'ActivityTemplates.background_location'
        db.add_column(u'wanglibao_activity_activitytemplates', 'background_location',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'ActivityTemplates.models_sequence'
        db.add_column(u'wanglibao_activity_activitytemplates', 'models_sequence',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=60, blank=True),
                      keep_default=False)


        # Changing field 'ActivityTemplates.teacher_desc'
        db.alter_column(u'wanglibao_activity_activitytemplates', 'teacher_desc', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True))

        # Changing field 'ActivityTemplates.desc_time'
        db.alter_column(u'wanglibao_activity_activitytemplates', 'desc_time', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True))

        # Changing field 'ActivityTemplates.rule_activity'
        db.alter_column(u'wanglibao_activity_activitytemplates', 'rule_activity', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'ActivityTemplates.rule_reward'
        db.alter_column(u'wanglibao_activity_activitytemplates', 'rule_reward', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'ActivityTemplates.rule_use'
        db.alter_column(u'wanglibao_activity_activitytemplates', 'rule_use', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'ActivityTemplates.reward_desc'
        db.alter_column(u'wanglibao_activity_activitytemplates', 'reward_desc', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'ActivityTemplates.desc'
        db.alter_column(u'wanglibao_activity_activitytemplates', 'desc', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True))

        # Changing field 'ActivityTemplates.introduce_img'
        db.alter_column(u'wanglibao_activity_activitytemplates', 'introduce_img', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True))

    def backwards(self, orm):

        # Changing field 'ActivityImages.desc_two'
        db.alter_column(u'wanglibao_activity_activityimages', 'desc_two', self.gf('django.db.models.fields.CharField')(max_length=1024))

        # Changing field 'ActivityImages.desc_one'
        db.alter_column(u'wanglibao_activity_activityimages', 'desc_one', self.gf('django.db.models.fields.CharField')(max_length=1024))
        # Adding field 'ActivityTemplates.introduce_desc'
        db.add_column(u'wanglibao_activity_activitytemplates', 'introduce_desc',
                      self.gf('ckeditor.fields.RichTextField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'ActivityTemplates.is_login'
        db.delete_column(u'wanglibao_activity_activitytemplates', 'is_login')

        # Deleting field 'ActivityTemplates.login_desc'
        db.delete_column(u'wanglibao_activity_activitytemplates', 'login_desc')

        # Deleting field 'ActivityTemplates.desc_img'
        db.delete_column(u'wanglibao_activity_activitytemplates', 'desc_img')

        # Deleting field 'ActivityTemplates.is_footer'
        db.delete_column(u'wanglibao_activity_activitytemplates', 'is_footer')

        # Deleting field 'ActivityTemplates.footer_color'
        db.delete_column(u'wanglibao_activity_activitytemplates', 'footer_color')

        # Deleting field 'ActivityTemplates.is_earning_one'
        db.delete_column(u'wanglibao_activity_activitytemplates', 'is_earning_one')

        # Deleting field 'ActivityTemplates.is_earning_two'
        db.delete_column(u'wanglibao_activity_activitytemplates', 'is_earning_two')

        # Deleting field 'ActivityTemplates.is_earning_three'
        db.delete_column(u'wanglibao_activity_activitytemplates', 'is_earning_three')

        # Deleting field 'ActivityTemplates.is_background'
        db.delete_column(u'wanglibao_activity_activitytemplates', 'is_background')

        # Deleting field 'ActivityTemplates.background_img'
        db.delete_column(u'wanglibao_activity_activitytemplates', 'background_img')

        # Deleting field 'ActivityTemplates.background_location'
        db.delete_column(u'wanglibao_activity_activitytemplates', 'background_location')

        # Deleting field 'ActivityTemplates.models_sequence'
        db.delete_column(u'wanglibao_activity_activitytemplates', 'models_sequence')


        # Changing field 'ActivityTemplates.teacher_desc'
        db.alter_column(u'wanglibao_activity_activitytemplates', 'teacher_desc', self.gf('ckeditor.fields.RichTextField')(null=True))

        # Changing field 'ActivityTemplates.desc_time'
        db.alter_column(u'wanglibao_activity_activitytemplates', 'desc_time', self.gf('django.db.models.fields.CharField')(default='', max_length=1024))

        # Changing field 'ActivityTemplates.rule_activity'
        db.alter_column(u'wanglibao_activity_activitytemplates', 'rule_activity', self.gf('ckeditor.fields.RichTextField')(null=True))

        # Changing field 'ActivityTemplates.rule_reward'
        db.alter_column(u'wanglibao_activity_activitytemplates', 'rule_reward', self.gf('ckeditor.fields.RichTextField')(null=True))

        # Changing field 'ActivityTemplates.rule_use'
        db.alter_column(u'wanglibao_activity_activitytemplates', 'rule_use', self.gf('ckeditor.fields.RichTextField')(null=True))

        # Changing field 'ActivityTemplates.reward_desc'
        db.alter_column(u'wanglibao_activity_activitytemplates', 'reward_desc', self.gf('ckeditor.fields.RichTextField')(null=True))

        # Changing field 'ActivityTemplates.desc'
        db.alter_column(u'wanglibao_activity_activitytemplates', 'desc', self.gf('django.db.models.fields.CharField')(default='', max_length=1024))

        # Changing field 'ActivityTemplates.introduce_img'
        db.alter_column(u'wanglibao_activity_activitytemplates', 'introduce_img', self.gf('ckeditor.fields.RichTextField')(null=True))

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
            'desc_one': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'desc_two': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
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
            'send_type': ('django.db.models.fields.CharField', [], {'default': "u'\\u7cfb\\u7edf'", 'max_length': '20'}),
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
            'background_img': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'background_location': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'banner': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'desc_img': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'desc_time': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'footer_color': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'introduce_img': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'is_activity_desc': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '20'}),
            'is_background': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '20'}),
            'is_earning_one': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_earning_three': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_earning_two': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_footer': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '20'}),
            'is_introduce': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '20'}),
            'is_login': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_reward': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '20'}),
            'is_rule_activity': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '20'}),
            'is_rule_reward': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '20'}),
            'is_rule_use': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '20'}),
            'is_teacher': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '20'}),
            'location': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'login_desc': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'logo_other': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'models_sequence': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'reward_desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'reward_img': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'rule_activity': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'rule_reward': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'rule_use': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'teacher_desc': ('django.db.models.fields.CharField', [], {'default': "' |*| |*| |*| |*| '", 'max_length': '1024', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['wanglibao_activity']