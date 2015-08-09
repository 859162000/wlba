# -*- coding: utf-8 -*-

from django.db import models


class PhoneLocation(models.Model):

    tel = models.IntegerField(verbose_name=u"号码前缀", max_length=7, unique=True, blank=False)
    province = models.CharField(verbose_name=u"省", max_length=20)
    city = models.CharField(verbose_name=u"市", max_length=20)
    sp = models.CharField(verbose_name=u"运营商", max_length=20)

    class Meta:
        verbose_name_plural = u"手机号码归属地"
