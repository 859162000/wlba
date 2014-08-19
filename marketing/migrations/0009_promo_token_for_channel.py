# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from wanglibao_profile.models import WanglibaoUserProfile


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName". 
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        promo_tokens = [
            'JOLzDzF6St-9oT44fRJJrA',
            'KniDAYLIQDaq79KHFY9VtQ',
            '-EHROzq2Q3C8GK_DGajWwA',
            '5a4IglGdQHmeZZMswr4xpQ',
            'Xw54GVERS3qVIBZ2iKw6TA',
            '8DMQYs3JSB2BXgaAetfS7Q',
            'y8-IPXEKQA2cLN0xkdvIPg',
            '8zJYu37RRMC7z2PhTsnPMA',
            'K8On6OlEQ5mqFxhpRHv_9w',
            'NCNlCQyHSGiOjkvwsdxMUg',
            'TL86KmhJShuqyBO0ZxR17A',
            'O_EF4TfOT9GznnHBPltzEg',
            'jNk9AwUqR0CWEE0q_fpnLQ',
            'KINYj2WIR62uYcU5F13YpQ',
            'FggkFXqRQj6dFLdZfd-DDQ',
            'bhA7mtpFSBeRiKGGO_scKw',
            'luZD1lSOTLS8V2e-wiDzMg',
            'qar1FqwYRrSTE2uQ3fDh3Q',
            'RsKt14LrR7ytEuM5s9jGlA',
            'io8XTih2Rm-wEbVz6xTi6Q',
        ]

        for index, token in enumerate(promo_tokens):
            user = orm['auth.user']()
            user.username = 'channel_%d' % (index + 1)
            user.save()

            promo_token = orm.PromotionToken()
            promo_token.user = user
            promo_token.token = token
            promo_token.save()

    def backwards(self, orm):
        "Write your backwards methods here."

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
        u'marketing.introducedby': {
            'Meta': {'object_name': 'IntroducedBy'},
            'bought_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'gift_send_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'introduced_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'introduces'", 'to': u"orm['auth.User']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'marketing.newsandreport': {
            'Meta': {'ordering': "['-score']", 'object_name': 'NewsAndReport'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'marketing.promotiontoken': {
            'Meta': {'object_name': 'PromotionToken'},
            'token': ('django.db.models.fields.CharField', [], {'default': "'inowKfcuQ2y9jiqHcdxb-A'", 'max_length': '64', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
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
        }
    }

    complete_apps = ['marketing']
    symmetrical = True
