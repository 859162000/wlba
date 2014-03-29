from django.db import models
from django.utils import timezone
from trust.models import Trust
from wanglibao_bank_financing.models import BankFinancing
from wanglibao_fund.models import Fund


class HotTrust(models.Model):
    trust = models.OneToOneField(Trust)
    hot_score = models.IntegerField(help_text="How hot is this")
    added = models.DateTimeField(help_text="When this guy appear in hot list",
                                 default=timezone.now,
                                 null=True)

    class Meta:
        ordering = ['-added']

    def __unicode__(self):
        return u'%s score: %d' % (self.trust.name, self.hot_score)


class HotFinancing(models.Model):
    bank_financing = models.OneToOneField(BankFinancing)
    hot_score = models.IntegerField(help_text="How hot is this")
    added = models.DateTimeField(help_text="When this guy appear in hot list",
                                 default=timezone.now,
                                 null=True)

    class Meta:
        ordering = ['-added']

    def __unicode__(self):
        return u'%s score: %d' % (self.bank_financing.name, self.hot_score)


class HotFund(models.Model):
    fund = models.OneToOneField(Fund)
    hot_score = models.IntegerField(help_text="How hot is this")
    added = models.DateTimeField(help_text="When this guy appear in hot list",
                                 default=timezone.now,
                                 null=True)

    class Meta:
        ordering = ['-added']

    def __unicode__(self):
        return u'%s score: %d' % (self.fund.name, self.hot_score)