# encoding:utf8
import json
from django.contrib.auth import get_user_model
from django.db import models
from jsonfield import JSONField


class Order(models.Model):
    """
    The main order model
    """

    type = models.CharField(max_length=64, verbose_name=u'订单类型')
    status = models.CharField(max_length=64, verbose_name=u'订单状态')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=u'订单创建时间')

    # Field for storing extra data
    extra_data = JSONField(blank=True)

    def __unicode__(self):
        return u"%s %s %s" % (str(self.id), self.type, unicode(json.dumps(self.extra_data)))


class OrderNote(models.Model):
    order = models.ForeignKey(Order, related_name='notes', verbose_name=u'订单')
    user = models.ForeignKey(get_user_model(), null=True, verbose_name=u'用户')

    # System generated note can't be edited

    type = models.CharField(max_length=64, verbose_name=u'流水类型')
    message = models.TextField(u'流水信息')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_data = JSONField(blank=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.message[:50], self.user)
