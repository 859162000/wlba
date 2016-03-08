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
    class Meta:
        model = PayInfo
