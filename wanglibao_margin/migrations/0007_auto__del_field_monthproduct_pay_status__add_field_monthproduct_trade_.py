# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'MonthProduct.pay_status'
        db.delete_column(u'wanglibao_margin_monthproduct', 'pay_status')

        # Adding field 'MonthProduct.trade_status'
        db.add_column(u'wanglibao_margin_monthproduct', 'trade_status',
                      self.gf('django.db.models.fields.CharField')(default='NEW', max_length=8),
                      keep_default=False)

        # Adding field 'AssignmentOfClaims.trade_status'
        db.add_column(u'wanglibao_margin_assignmentofclaims', 'trade_status',
                      self.gf('django.db.models.fields.CharField')(default='NEW', max_length=8),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'MonthProduct.pay_status'
        db.add_column(u'wanglibao_margin_monthproduct', 'pay_status',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'MonthProduct.trade_status'
        db.delete_column(u'wanglibao_margin_monthproduct', 'trade_status')

        # Deleting field 'AssignmentOfClaims.trade_status'
        db.delete_column(u'wanglibao_margin_assignmentofclaims', 'trade_status')


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
        u'wanglibao_margin.assignmentofclaims': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'AssignmentOfClaims'},
            'buy_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'buy_price_source': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'buyer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assignment_buyer'", 'to': u"orm['auth.User']"}),
            'buyer_order_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'buyer_token': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'fee': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'premium_fee': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'product_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sell_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'sell_price_source': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'seller': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assignment_seller'", 'to': u"orm['auth.User']"}),
            'seller_order_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'seller_token': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'trade_status': ('django.db.models.fields.CharField', [], {'default': "'NEW'", 'max_length': '8'}),
            'trading_fee': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'})
        },
        u'wanglibao_margin.margin': {
            'Meta': {'object_name': 'Margin'},
            'freeze': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '20', 'decimal_places': '2'}),
            'invest': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '20', 'decimal_places': '2'}),
            'margin': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '20', 'decimal_places': '2'}),
            'uninvested': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '20', 'decimal_places': '2'}),
            'uninvested_freeze': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '20', 'decimal_places': '2'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'withdrawing': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '20', 'decimal_places': '2'})
        },
        u'wanglibao_margin.marginrecord': {
            'Meta': {'ordering': "['-create_time']", 'object_name': 'MarginRecord'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'catalog': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'margin_current': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'order_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'})
        },
        u'wanglibao_margin.monthproduct': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'MonthProduct'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'amount_source': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'cancel_status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'red_packet': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'red_packet_type': ('django.db.models.fields.CharField', [], {'default': "'-1'", 'max_length': '32', 'db_index': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'db_index': 'True'}),
            'trade_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'trade_status': ('django.db.models.fields.CharField', [], {'default': "'NEW'", 'max_length': '8'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'month_product_buyer'", 'to': u"orm['auth.User']"})
        },
        u'wanglibao_margin.phprefundrecord': {
            'Meta': {'ordering': "['-create_at']", 'object_name': 'PhpRefundRecord'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'catalog': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '32', 'db_index': 'True'}),
            'create_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'margin_current': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'refund_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'})
        }
    }

    complete_apps = ['wanglibao_margin']