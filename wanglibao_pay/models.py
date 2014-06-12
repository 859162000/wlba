# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.db import models


class PayInfo(models.Model):
    type = models.CharField(verbose_name=u'类型', help_text=u'充值：D 取款：W', max_length=5)
    amount = models.FloatField(verbose_name=u'金额')
    user = models.ForeignKey(get_user_model())
