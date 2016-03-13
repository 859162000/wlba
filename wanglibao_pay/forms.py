# coding=utf-8

import django.forms as forms
from django.contrib.auth.models import User
from django.utils import timezone
from .models import PayInfo


class RechargeForm(forms.Form):
    order_id = forms.IntegerField(error_messages={
        'required': u'订单号是必须的',
        'invalid': u'订单号必须是数字'
    })
    amount = forms.IntegerField(error_messages={
        'required': u'投资金额是必须的',
        'invalid': u'投资金额必须是数字'
    })
    user_id = forms.IntegerField(error_messages={
        'required': u'用户id是必须的',
        'invalid': u'用户id必须是数字'
    })
    recharge_at = forms.IntegerField(error_messages={
        'required': u'充值时间是必须的',
        'invalid': u'充值时间必须是数字'
    })
    status = forms.CharField(error_messages={
        'required': u'充值时间是必须的',
    })

    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise forms.ValidationError(
                code=10031,
                message=u'无效用户id',
            )

        return user

    def clean_recharge_at(self):
        recharge_at = self.cleaned_data['recharge_at']
        if len(str(recharge_at)) == 13:
            recharge_at = timezone.localtime(recharge_at)
        else:
            raise forms.ValidationError(
                code=10032,
                message=u'无效充值时间',
            )

        return recharge_at


class PayInfoForm(forms.ModelForm):
    type = forms.CharField(label=u'类型', error_messages={'required': u'请输入类型'})
    uuid = forms.CharField(label=u'唯一标示', error_messages={'required': u'请输入唯一标示'})
    amount = forms.DecimalField(label=u'实扣金额', error_messages={'required': u'请输入实扣金额'})
    fee = forms.DecimalField(label=u'手续费', error_messages={'required': u'请输入手续费'})
    management_fee = forms.DecimalField(label=u'资金管理费用', error_messages={'required': u'请输入资金管理费用'})
    management_amount = forms.DecimalField(label=u'资金管理金额', error_messages={'required': u'请输入资金管理金额'})
    total_amount = forms.DecimalField(label=u'总金额', error_messages={'required': u'请输入总金额'})
    create_time = forms.DateTimeField(label=u'创建时间', error_messages={'required': u'请输入创建时间'})
    status = forms.CharField(label=u'状态', error_messages={'required': u'请输入状态'})
    user_id = forms.IntegerField(label=u'用户id', error_messages={'required': u'请输入用户id'})
    order_id = forms.IntegerField(label=u'支付流水号', error_messages={'required': u'请输入支付流水号'})

    class Meta:
        model = PayInfo
