#!/usr/bin/env python
# encoding: utf8

from django.contrib.auth import get_user_model
from django.db import models


class IdVerification(models.Model):
    """
    This is a table stores all id verification info. The verify method should
    check this table first
    """

    id_number = models.CharField(u"身份证号", max_length=128, db_index=True)
    name = models.CharField(u"姓名", max_length=32)
    is_valid = models.BooleanField(u"验证结果", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s %s %d' % (self.id_number, self.name, self.is_valid)


class VerifyCounter(models.Model):
    """
    The table stores the count each user called the id verify api
    """

    user = models.OneToOneField(get_user_model())
    count = models.IntegerField(u'尝试认证次数', default=0)

    def __unicode__(self):
        return u'%s: %d' % (self.user.wanglibaouserprofile.phone, self.count)


class UserPushId(models.Model):
    """
        app push table, store all the user and all the device
    """
    user = models.ForeignKey(get_user_model(), null=True)
    device_type = models.CharField(max_length=20, verbose_name="设备类型")
    push_user_id = models.CharField(max_length=50, db_index=True)
    push_channel_id = models.CharField(max_length=50)


class Binding(models.Model):
    """
        third app bind table, store bind related
    """
    user = models.ForeignKey(get_user_model())
    btype = models.CharField(max_length=10, choices=(
        ('xunlei', 'xunlei'),
    ))
    bid = models.CharField(max_length=20, db_index=True)
    bname = models.CharField(max_length=50)
    gender = models.CharField(max_length=5, choices=(
        ("m", "m"),
        ("w", "w"),
        ("n", "n"),
    ))
    isvip = models.BooleanField(default=False, verbose_name=u"是否是vip")
    extra = models.CharField(max_length=200, default="")
    access_token = models.CharField(max_length=100)
    refresh_token = models.CharField(max_length=100)
    created_at = models.BigIntegerField(default=0, verbose_name=u'创建时间')
