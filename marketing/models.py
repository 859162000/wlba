# coding=utf-8
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from wanglibao_pay.util import get_a_uuid
from django.db import transaction

class NewsAndReport(models.Model):
    name = models.CharField(u'名字', max_length=128)
    link = models.URLField(u'链接', null=True)
    score = models.IntegerField(u'排名权重', default=0)
    created_at = models.DateTimeField(u'添加时间', auto_now_add=True)
    image = models.ImageField(u'图片', null=True, upload_to='news', blank=True)

    class Meta:
        ordering = ['-score']

    def __unicode__(self):
        return self.name


class SiteData(models.Model):
    invest_threshold = models.IntegerField(u'起投额（元）', default=100)
    p2p_total_earning = models.DecimalField(u'投资人总收益', max_digits=20, decimal_places=2, default=0)
    p2p_total_trade = models.DecimalField(u'累计交易额', max_digits=20, decimal_places=2, default=0)
    earning_rate = models.CharField(u'年化收益率', max_length=16, default=u'10%-15%')
    highest_earning_rate = models.FloatField(u'最高年化收益率(%)', default=15)
    demand_deposit_interest_rate = models.FloatField(u'活期存款利率(%)', default=0.35)
    one_year_interest_rate = models.FloatField(u'一年期存款利率(%)', default=3)
    product_release_time = models.CharField(u'产品发布时间', max_length=128, default=u'17:30')
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'起投额 %d 总收益 %f 累计交易额 %f' % (self.invest_threshold, float(self.p2p_total_earning), float(self.p2p_total_trade))

    @property
    def demand_rate_times(self):
        return int(self.highest_earning_rate / self.demand_deposit_interest_rate)

    @property
    def one_year_times(self):
        return int(self.highest_earning_rate / self.one_year_interest_rate)

# class InviteCode(models.Model):
#     code = models.CharField(u'邀请码', max_length=6, db_index=True, unique=True)
#     is_used = models.BooleanField(u'是否使用', default=False)
#
#     def __unicode__(self):
#         return self.code

#
# def get_a_invitecode():
#     with transaction.atomic():
#         invite_code = InviteCode.objects.select_for_update().filter(is_used=False).first()
#         invite_code.is_used = True
#         invite_code.save()
#         return invite_code.code



class PromotionToken(models.Model):
    user = models.OneToOneField(get_user_model(), primary_key=True)
    token = models.CharField(u'推广代码', max_length=64, db_index=True, default=get_a_uuid)

    def __unicode__(self):
        return self.token


class IntroducedBy(models.Model):
    user = models.ForeignKey(get_user_model())
    introduced_by = models.ForeignKey(get_user_model(), related_name='introduces')
    created_at = models.DateTimeField(u'创建时间', auto_now_add=True)
    bought_at = models.DateTimeField(u'第一次购买时间', null=True)
    gift_send_at = models.DateTimeField(u'奖品发放时间', null=True)


def generate_user_promo_token(sender, instance, **kwargs):
    if kwargs["created"]:
        p = PromotionToken()
        p.user = instance
        p.save()

post_save.connect(generate_user_promo_token, sender=get_user_model(), dispatch_uid="generate_promotion_token")


class TimelySiteData(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    p2p_margin = models.DecimalField(u'P2P余额', max_digits=20, decimal_places=2, default=0)
    freeze_amount = models.DecimalField(u'投资中冻结金额', max_digits=20, decimal_places=2, default=0)
    total_amount = models.DecimalField(u'总额', max_digits=20, decimal_places=2, default=0)
    user_count = models.IntegerField(u'用户总数', default=0)




