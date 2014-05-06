# encoding:utf-8
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class BuyInfo(models.Model):
    type = models.CharField(help_text=u'产品种类', max_length=64)
    item_id = models.IntegerField(help_text=u'产品id')
    item_name = models.CharField(help_text=u'产品名称', blank=True, max_length=64)
    amount = models.IntegerField(help_text=u'金额（元）', default=0)
    user = models.ForeignKey(get_user_model())
    verify_info = models.CharField(help_text=u'验证消息，可以用来与购买放进行验证的编号（比如，数米的申请编号）', blank=True, max_length=128)
    created_at = models.DateTimeField(default=timezone.now, help_text=u'购买发生时间', blank=True)

    def __unicode__(self):
        return u'%s买了%s %s %d元' % (self.user.wanglibaouserprofile.phone, self.type, self.item_name, self.amount)
