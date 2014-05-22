# encoding:utf-8
from random import randrange
from django.db import models


class ProductBase(models.Model):
    bought_people_count = models.IntegerField(default=0, help_text=u'购买人数')
    bought_count = models.IntegerField(default=0, help_text=u'购买次数')
    bought_amount = models.BigIntegerField(default=0, help_text=u'产品购买总金额（元）')

    bought_count_random = models.FloatField(default=lambda (): randrange(101, 121)/100.0, help_text=u'产品购买笔数随机数')
    bought_amount_random = models.FloatField(default=lambda (): randrange(90, 131)/100.0, help_text=u'人均购买金额随机数')

    class Meta:
        abstract = True