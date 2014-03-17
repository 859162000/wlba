# encoding: utf-8
from datetime import datetime
from django.contrib.auth import get_user_model
from django.db import models


class PreOrder(models.Model):
    product_name = models.CharField(max_length=256)
    product_type = models.CharField(max_length=256, choices=(
        ('trust', 'trust'),
        ('financing', 'financing'),
        ('fund', 'fund'),
    ))
    created_at = models.DateTimeField(default=datetime.now)
    product_url = models.TextField(default='')
    user_name = models.CharField(max_length=64)
    phone = models.CharField(max_length=64)
    user = models.ForeignKey(get_user_model(), blank=True, null=True)
    status = models.CharField(max_length=16, default=u'待处理', choices=(
        (u'待处理', u'待处理'),
        (u'处理中', u'处理中'),
        (u'处理完', u'处理完'),
        (u'待跟进', u'待跟进')
    ))
    process_result = models.CharField(max_length=16, blank=True, default=u"跟进", choices=(
        (u'跟进', u'跟进'),
        (u'号码错误', u'号码错误'),
        (u'骚扰', u'骚扰'),
        (u'资讯', u'资讯'),
        (u'其他', u'其他')
    ))
    note = models.TextField(default="", blank=True)

    def __unicode__(self):
        return "%s %s %s" % (self.phone, self.user_name, self.product_name)
