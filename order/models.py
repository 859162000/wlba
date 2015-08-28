# encoding:utf8
import json
import collections
#from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from wanglibao.fields import JSONFieldUtf8


class Order(models.Model):
    """
    The main order model
    """
    PAY_ORDER = 'pay'
    WITHDRAW_ORDER = 'withdraw'
    ACTIVITY = 'activity'
    INTEREST_COUPON = 'interest_coupon'

    type = models.CharField(max_length=64, verbose_name=u'订单类型')
    status = models.CharField(max_length=64, verbose_name=u'订单状态')

    # Parent Order
    parent = models.ForeignKey("self", null=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=u'订单创建时间')

    # Field for storing extra data
    extra_data = JSONFieldUtf8(blank=True, load_kwargs={'object_pairs_hook': collections.OrderedDict})

    def __unicode__(self):
        return u"%s %s %s" % (str(self.id), self.type, unicode(json.dumps(self.extra_data)))


class OrderNote(models.Model):
    order = models.ForeignKey(Order, related_name='notes', verbose_name=u'订单', null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, null=True, verbose_name=u'用户', on_delete=models.SET_NULL)

    # System generated note can't be edited

    type = models.CharField(max_length=64, verbose_name=u'流水类型')
    message = models.TextField(u'流水信息')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_data = JSONFieldUtf8(blank=True, load_kwargs={'object_pairs_hook': collections.OrderedDict})

    class Meta:
        ordering = ['-created_at']

    def __unicode__(self):
        return u'%s (%s)' % (self.message[:50], self.user)
