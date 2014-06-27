# encoding:utf-8
from random import randrange
from django.db import models


class ProductBase(models.Model):
    bought_people_count = models.IntegerField(default=0, help_text=u'购买人数', editable=False)
    bought_count = models.IntegerField(default=0, help_text=u'购买次数', editable=False)
    bought_amount = models.BigIntegerField(default=0, help_text=u'产品购买总金额（元）', editable=False)

    bought_count_random = models.FloatField(default=0, help_text=u'产品购买笔数随机数', editable=False)
    bought_amount_random = models.FloatField(default=0, help_text=u'人均购买金额随机数', editable=False)

    class Meta:
        abstract = True