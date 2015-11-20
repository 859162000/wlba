# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ExperienceProduct'
        db.create_table(u'experience_gold_experienceproduct', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('period', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('expected_earning_rate', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=20)),
            ('isvalid', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'experience_gold', ['ExperienceProduct'])

        # Adding model 'ExperienceEvent'
        db.create_table(u'experience_gold_experienceevent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('amount', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True)),
            ('give_mode', self.gf('django.db.models.fields.CharField')(default=u'\u6ce8\u518c', max_length=20, db_index=True)),
            ('give_platform', self.gf('django.db.models.fields.CharField')(default=u'\u5168\u5e73\u53f0', max_length=10)),
            ('target_channel', self.gf('django.db.models.fields.CharField')(default='', max_length=500, blank=True)),
            ('available_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('unavailable_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('invalid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'experience_gold', ['ExperienceEvent'])

        # Adding model 'ExperienceEventRecord'
        db.create_table(u'experience_gold_experienceeventrecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['experience_gold.ExperienceEvent'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('apply', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('apply_platform', self.gf('django.db.models.fields.CharField')(default='', max_length=20)),
            ('apply_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('apply_amount', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True)),
        ))
        db.send_create_signal(u'experience_gold', ['ExperienceEventRecord'])

        # Adding model 'ExperienceAmortization'
        db.create_table(u'experience_gold_experienceamortization', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='experience_product_subs', to=orm['experience_gold.ExperienceProduct'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('term', self.gf('django.db.models.fields.IntegerField')()),
            ('term_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('principal', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('interest', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('settled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('settlement_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
        ))
        db.send_create_signal(u'experience_gold', ['ExperienceAmortization'])


    def backwards(self, orm):
        # Deleting model 'ExperienceProduct'
        db.delete_table(u'experience_gold_experienceproduct')

        # Deleting model 'ExperienceEvent'
        db.delete_table(u'experience_gold_experienceevent')

        # Deleting model 'ExperienceEventRecord'
        db.delete_table(u'experience_gold_experienceeventrecord')

        # Deleting model 'ExperienceAmortization'
        db.delete_table(u'experience_gold_experienceamortization')


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
        u'experience_gold.experienceamortization': {
            'Meta': {'object_name': 'ExperienceAmortization'},
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'principal': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'experience_product_subs'", 'to': u"orm['experience_gold.ExperienceProduct']"}),
            'settled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'settlement_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'term': ('django.db.models.fields.IntegerField', [], {}),
            'term_date': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'experience_gold.experienceevent': {
            'Meta': {'object_name': 'ExperienceEvent'},
            'amount': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'available_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'give_mode': ('django.db.models.fields.CharField', [], {'default': "u'\\u6ce8\\u518c'", 'max_length': '20', 'db_index': 'True'}),
            'give_platform': ('django.db.models.fields.CharField', [], {'default': "u'\\u5168\\u5e73\\u53f0'", 'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'target_channel': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500', 'blank': 'True'}),
            'unavailable_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'experience_gold.experienceeventrecord': {
            'Meta': {'object_name': 'ExperienceEventRecord'},
            'apply': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'apply_amount': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True'}),
            'apply_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'apply_platform': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experience_gold.ExperienceEvent']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'experience_gold.experienceproduct': {
            'Meta': {'object_name': 'ExperienceProduct'},
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'expected_earning_rate': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isvalid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'period': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['experience_gold']