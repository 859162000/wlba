# encoding:utf8

from django.db import models


# Create your models here.
class Formular(models.Model):
    bought_people_count_gt_521 = models.TextField(verbose_name=u'收益率大于5.21的购买人数公式', blank=True, default=u"0", help_text=u'x = 7日年化, d = 据2014-5-15的日期数, ra = 本货币基金的购买笔数随机数, rp = 本货币基金的人均购买随机数')
    bought_people_count_le_521 = models.TextField(verbose_name=u'收益率小于5.21的购买人数公式', blank=True, default=u"0", help_text=u'x = 7日年化, d = 据2014-5-15的日期数, ra = 本货币基金的购买笔数随机数, rp = 本货币基金的人均购买随机数')
    bought_count = models.TextField(verbose_name=u'购买笔数', blank=True, default=u'0', help_text=u'x = 7日年化, d = 据2014-5-15的日期数, ra = 本货币基金的购买笔数随机数, rp = 本货币基金的人均购买随机数, count = 购买人数')
    bought_amount_per_people = models.TextField(verbose_name=u'人均购买金额', blank=True, default=u'0', help_text=u'x = 7日年化, d = 据2014-5-15的日期数, ra = 本货币基金的购买笔数随机数, rp = 本货币基金的人均购买随机数, count = 购买人数')

    def __unicode__(self):
        return u'公式'