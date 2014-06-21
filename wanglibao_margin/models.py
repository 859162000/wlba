# encoding: utf-8
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model


# Create your models here.
class Margin(models.Model):
    user = models.OneToOneField(get_user_model(), primary_key=True)
    margin = models.DecimalField(verbose_name=u'用户余额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    freeze = models.DecimalField(verbose_name=u'冻结金额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    withdrawing = models.DecimalField(verbose_name=u'提款中金额', max_digits=20, decimal_places=2,
                                        default=Decimal('0.00'))

    def __unicode__(self):
        return '%s margin: %s, freeze: %s' % (self.user, self.margin, self.freeze)

    def has_margin(self, amount):
        amount = Decimal(amount)
        if amount <= self.margin:
            return True
        return False


class MarginRecord(models.Model):
    catalog = models.CharField(verbose_name=u'流水类型', max_length=100)
    order_id = models.IntegerField(verbose_name=u'相关订单编号')
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    create_time = models.DateTimeField(verbose_name=u'流水时间', auto_now_add=True)

    amount = models.DecimalField(verbose_name=u'发生金额', max_digits=20, decimal_places=2)
    margin_current = models.DecimalField(verbose_name=u'用户后余额', max_digits=20, decimal_places=2)
    description = models.CharField(verbose_name=u'摘要', max_length=1000, default=u'')

    def __unicode__(self):
        return u'%s , %s' % (self.catalog, self.user)
