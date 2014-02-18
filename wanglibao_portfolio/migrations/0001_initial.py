# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ProductType'
        db.create_table(u'wanglibao_portfolio_producttype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('average_earning_rate', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('average_risk_score', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
        ))
        db.send_create_signal(u'wanglibao_portfolio', ['ProductType'])

        # Adding model 'Portfolio'
        db.create_table(u'wanglibao_portfolio_portfolio', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('risk_score', self.gf('django.db.models.fields.SmallIntegerField')(default=2)),
            ('asset_min', self.gf('django.db.models.fields.FloatField')()),
            ('asset_max', self.gf('django.db.models.fields.FloatField')()),
            ('period_min', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('period_max', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('investment_preference', self.gf('django.db.models.fields.CharField')(default=u'\u5e73\u8861\u578b', max_length=16)),
            ('expected_earning_rate', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'wanglibao_portfolio', ['Portfolio'])

        # Adding model 'PortfolioProductEntry'
        db.create_table(u'wanglibao_portfolio_portfolioproductentry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('portfolio', self.gf('django.db.models.fields.related.ForeignKey')(related_name='products', to=orm['wanglibao_portfolio.Portfolio'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_portfolio.ProductType'])),
            ('value', self.gf('django.db.models.fields.FloatField')()),
            ('type', self.gf('django.db.models.fields.CharField')(default='percent', max_length=16)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'wanglibao_portfolio', ['PortfolioProductEntry'])

        # Adding model 'UserPortfolio'
        db.create_table(u'wanglibao_portfolio_userportfolio', (
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'wanglibao_portfolio', ['UserPortfolio'])

        # Adding M2M table for field portfolio on 'UserPortfolio'
        m2m_table_name = db.shorten_name(u'wanglibao_portfolio_userportfolio_portfolio')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userportfolio', models.ForeignKey(orm[u'wanglibao_portfolio.userportfolio'], null=False)),
            ('portfolio', models.ForeignKey(orm[u'wanglibao_portfolio.portfolio'], null=False))
        ))
        db.create_unique(m2m_table_name, ['userportfolio_id', 'portfolio_id'])


    def backwards(self, orm):
        # Deleting model 'ProductType'
        db.delete_table(u'wanglibao_portfolio_producttype')

        # Deleting model 'Portfolio'
        db.delete_table(u'wanglibao_portfolio_portfolio')

        # Deleting model 'PortfolioProductEntry'
        db.delete_table(u'wanglibao_portfolio_portfolioproductentry')

        # Deleting model 'UserPortfolio'
        db.delete_table(u'wanglibao_portfolio_userportfolio')

        # Removing M2M table for field portfolio on 'UserPortfolio'
        db.delete_table(db.shorten_name(u'wanglibao_portfolio_userportfolio_portfolio'))


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
        u'wanglibao_portfolio.portfolio': {
            'Meta': {'object_name': 'Portfolio'},
            'asset_max': ('django.db.models.fields.FloatField', [], {}),
            'asset_min': ('django.db.models.fields.FloatField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'expected_earning_rate': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investment_preference': ('django.db.models.fields.CharField', [], {'default': "u'\\u5e73\\u8861\\u578b'", 'max_length': '16'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'period_max': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'period_min': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'risk_score': ('django.db.models.fields.SmallIntegerField', [], {'default': '2'})
        },
        u'wanglibao_portfolio.portfolioproductentry': {
            'Meta': {'object_name': 'PortfolioProductEntry'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'portfolio': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'products'", 'to': u"orm['wanglibao_portfolio.Portfolio']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_portfolio.ProductType']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'percent'", 'max_length': '16'}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        u'wanglibao_portfolio.producttype': {
            'Meta': {'object_name': 'ProductType'},
            'average_earning_rate': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'average_risk_score': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'wanglibao_portfolio.userportfolio': {
            'Meta': {'object_name': 'UserPortfolio'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'portfolio': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['wanglibao_portfolio.Portfolio']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['wanglibao_portfolio']