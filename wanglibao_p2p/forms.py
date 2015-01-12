# coding=utf-8
from captcha.fields import CaptchaField
import django.forms as forms
from wanglibao_p2p.models import P2PProduct


class PurchaseForm(forms.Form):
    product = forms.ModelChoiceField(queryset=P2PProduct.objects.all(), widget=forms.HiddenInput())
    amount = forms.IntegerField(error_messages={
        'required': u'购买金额不能为空',
        'invalid': u'请输入整数'
    })

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount % 100 != 0:
            raise forms.ValidationError(u'购买金额必须为100的整数倍')
        if amount <= 0:
            raise forms.ValidationError(u'购买金额不能为负数')

        return amount

class BillForm(forms.Form):
    product = forms.ModelChoiceField(queryset=P2PProduct.objects.all(), widget=forms.HiddenInput())
    amount = forms.IntegerField(error_messages={
        'required': u'购买金额不能为空'
    })

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError(u'购买金额不能为负数')

        return amount
