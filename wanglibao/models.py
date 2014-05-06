# encoding:utf-8
from django.db import models


class ProductBase(models.Model):
    bought_people_count = models.IntegerField(default=0, help_text=u'购买人数')
    bought_count = models.IntegerField(default=0, help_text=u'购买次数')
    bought_amount = models.BigIntegerField(default=0, help_text=u'产品购买总金额（元）')

    class Meta:
        abstract = True