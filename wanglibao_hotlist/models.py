# encoding:utf-8

from django.db import models
from django.utils import timezone
from trust.models import Trust
from wanglibao_bank_financing.models import BankFinancing
from wanglibao_fund.models import Fund
from wanglibao_p2p.models import P2PProduct


class HotItemBase(models.Model):
    hot_score = models.IntegerField(default=0, help_text=u'热力指数 越高排名越靠前')
    added = models.DateTimeField(help_text=u'创建时间', default=timezone.now, null=True)

    class Meta:
        abstract = True
        ordering = ['-hot_score']


class HotTrust(HotItemBase):
    trust = models.OneToOneField(Trust)

    def __unicode__(self):
        return u'%s score: %d' % (self.trust.name, self.hot_score)


class HotFinancing(HotItemBase):
    bank_financing = models.OneToOneField(BankFinancing)

    def __unicode__(self):
        return u'%s score: %d' % (self.bank_financing.name, self.hot_score)


class HotFund(HotItemBase):
    fund = models.OneToOneField(Fund)

    def __unicode__(self):
        return u'%s score: %d' % (self.fund.name, self.hot_score)


class MobileHotFund(HotItemBase):
    """
    The hot fund list for mobile
    """
    fund = models.OneToOneField(Fund)

    def __unicode__(self):
        return u'%s score: %d' % (self.fund.name, self.hot_score)


class MobileHotTrust(HotItemBase):
    """
    The hot trust list for mobile
    """
    trust = models.OneToOneField(Trust)

    def __unicode__(self):
        return u'%s score: %d' % (self.trust.name, self.hot_score)


class MobileMainPage(HotItemBase):
    """
    The mobile main page, now it is fund, in future it may contain other products
    TODO Figure out a better way to fullfil the hot list requirements
    """
    item = models.OneToOneField(Fund)

    def __unicode__(self):
        return u'%s score: %d' % (self.item.name, self.hot_score)


class MobileMainPageP2P(HotItemBase):
    item = models.OneToOneField(P2PProduct)

    def __unicode__(self):
        return u'%s score: %d' % (self.item.name, self.hot_score)
