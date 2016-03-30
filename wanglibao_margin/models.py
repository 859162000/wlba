# encoding: utf-8
from decimal import Decimal
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User


# Create your models here.
class Margin(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    margin = models.DecimalField(u'用户余额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    freeze = models.DecimalField(u'冻结金额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    withdrawing = models.DecimalField(u'提款中金额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    invest = models.DecimalField(u'已投资金额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    uninvested = models.DecimalField(u'充值未投资金额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    uninvested_freeze = models.DecimalField(u'充值未投资冻结金额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    # updated_time = models.DateTimeField(u'更新时间', auto_now=True)

    def __unicode__(self):
        return u'%s margin: %s, freeze: %s' % (self.user, self.margin, self.freeze)

    def has_margin(self, amount):
        amount = Decimal(amount)
        if amount <= self.margin:
            return True
        return False


class MarginRecord(models.Model):
    catalog = models.CharField(u'流水类型', max_length=100)
    order_id = models.IntegerField(u'相关订单编号', null=True, db_index=True)
    user_id = models.IntegerField(u'用户id', max_length=50, db_index=True)
    create_time = models.DateTimeField(u'流水时间', auto_now_add=True)

    amount = models.DecimalField(u'发生金额', max_digits=20, decimal_places=2)
    margin_current = models.DecimalField(u'用户后余额', max_digits=20, decimal_places=2)
    description = models.CharField(u'摘要', max_length=1000, null=True, blank=True)

    def __unicode__(self):
        return u'%s , %s, 交易金额%s, 余额%s' % (self.catalog, self.user, self.amount, self.margin_current)

    class Meta:
        ordering = ['-create_time']


def create_user_margin(sender, **kwargs):
    """
    create user margin after user object created.
    :param sender:
    :param kwargs:
    :return:
    """
    if kwargs['created']:
        user = kwargs['instance']
        margin = Margin(user=user)
        margin.save()


post_save.connect(create_user_margin, sender=User, dispatch_uid='users-margin-creation-signal')
