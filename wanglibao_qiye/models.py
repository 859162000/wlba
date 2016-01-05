# encoding: utf-8

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from wanglibao_pay.models import Bank, Card

User = get_user_model()


class EnterpriseUserProfile(models.Model):
    """
    企业用户信息
    """

    STATUS = (
        (u'待审核', u'待审核'),
        (u'审核中', u'审核中'),
        (u'审核失败', u'审核失败'),
        (u'审核通过', u'审核通过'),
    )

    user = models.ForeignKey(User, primary_key=True)
    company_name = models.CharField(u'公司名称', max_length=30)
    business_license = models.ImageField(u'营业执照', upload_to='enterprise/images')
    registration_cert = models.ImageField(u'税务登记证', upload_to='enterprise/images')
    certigier_name = models.CharField(u'授权人姓名', max_length=12)
    certigier_phone = models.CharField(u'授权人手机号', max_length=64)
    company_address = models.TextField(u'公司地址', max_length=255)
    bank_card_no = models.CharField(u'公司账户账号', max_length=64)
    bank_account_name = models.CharField(u'公司账户名称', max_length=30)
    deposit_bank_province = models.CharField(u'公司开户行所在省份', max_length=10)
    deposit_bank_city = models.CharField(u'公司开户行所在市县', max_length=10)
    bank_branch_address = models.CharField(u'开户行支行所在地', max_length=100)
    modify_time = models.DateTimeField(u'最近修改时间', auto_now_add=True)
    created_time = models.DateTimeField(u'创建时间', auto_now=True)
    description = models.TextField(u'创建时间', max_length=255, null=True, blank=True)
    status = models.CharField(u'审核状态', max_length=10, default=u'待审核', choices=STATUS)
    bank = models.ForeignKey(Bank, verbose_name=u'所属银行')

    def save(self, *args, **kwargs):
        user_profile = self.user.wanglibaouserprofile
        if self.status == u'审核通过':
            user_profile.id_is_valid = True
            user_profile.id_valid_time = timezone.now()
            card = Card()
            card.bank = self.bank
            card.no = self.bank_card_no
            card.user = self.user
            card.is_default = True
            card.is_bind_huifu = True
            # FixMe, 同卡进出
            # card.is_the_one_card = True
            card.save()
        else:
            user_profile.id_is_valid = False

        user_profile.save()
        super(EnterpriseUserProfile, self).save(*args, **kwargs)
