from rest_framework.renderers import JSONRenderer
from rest_framework.serializers import ModelSerializer
from django.db import models
import elasticsearch
import logging

logger = logging.getLogger(__name__)


class Issuer(models.Model):
    name = models.TextField()
    short_name = models.TextField()
    english_name = models.TextField()

    registered_capital = models.IntegerField(verbose_name="registered capital in W")

    legal_presentative = models.TextField()
    chairman_of_board = models.TextField()
    manager = models.TextField()

    founded_at = models.DateField()
    appear_on_market = models.BooleanField()
    geo_region = models.TextField()

    shareholder_background = models.TextField()
    major_stockholder = models.TextField()
    shareholders = models.TextField()

    note = models.TextField() # Some note on the company

    business_range = models.TextField()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Issuer, self).save(*args, **kwargs)

        class IssuerSerializer(ModelSerializer):
            class Meta:
                model = Issuer

        serializer = IssuerSerializer(self)
        json = JSONRenderer().render(serializer.data)
        es = elasticsearch.Elasticsearch()
        es.index(index="wanglibao", doc_type="issuer", body=json, id=self.id)


class Trust (models.Model):
    name = models.TextField()
    short_name = models.CharField(max_length=256)
    expected_earning_rate = models.FloatField()
    brief = models.TextField()
    issuer = models.ForeignKey(Issuer, verbose_name="the issuer of this trust")
    available_region = models.TextField()
    scale = models.IntegerField(verbose_name="the scale of this trust, in the unit of RMB")

    investment_threshold = models.FloatField(verbose_name="the investment threshold in 10k")
    period = models.FloatField(verbose_name="the period in months")
    issue_date = models.DateField()
    type = models.TextField(verbose_name="trust type")

    earning_description = models.TextField()
    note = models.TextField(verbose_name="note on this trust")
    usage = models.CharField(max_length=100, verbose_name="usage", choices=(
        ('estate', 'estate'),
        ('finance', 'finance'),
        ('infrastructure', 'infrastructure'),
        ('others', 'others')
    ))
    usage_description = models.TextField()

    risk_management = models.TextField()
    payment = models.TextField()

    product_name = models.TextField()
    related_info = models.TextField()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Trust, self).save(*args, **kwargs)

        class TrustSerializer(ModelSerializer):
            class Meta:
                model = Trust

        serializer = TrustSerializer(self)
        json = JSONRenderer().render(serializer.data)
        es = elasticsearch.Elasticsearch()
        es.index(index="wanglibao", doc_type="trust", body=json, id=self.id)