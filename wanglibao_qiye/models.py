# encoding: utf-8
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class EnterpriseUserProfile(models.Model):
    user = models.ForeignKey(User, primary_key=True)
    company_name = models.CharField(u'公司名称', max_length=30)
    business_license = models.ImageField(u'营业执照', upload_to='enterprise/images')
    registration_cert = models.ImageField(u'税务登记证', upload_to='enterprise/images')
    certigier_name = models.CharField(u'授权人姓名', max_length=12)
    certigier_phone = models.IntegerField(u'授权人手机号', max_length=64)
    company_address = models.TextField(u'公司地址', max_length=255)
    company_account = models.CharField(u'公司账户账号', max_length=64)
    company_account_name = models.CharField(u'公司账户名称', max_length=30)
    deposit_bank_province = models.CharField(u'公司开户行所在省份', max_length=10)
    deposit_bank_city = models.CharField(u'公司开户行所在市县', max_length=10)
    bank_branch_address = models.CharField(u'开户行支行所在地', max_length=100)
    modify_time = models.DateTimeField(u'最近修改时间', auto_now_add=True)
    created_time = models.DateTimeField(u'创建时间', auto_now=True)
    description = models.TextField(u'创建时间', max_length=255, null=True, blank=True)
