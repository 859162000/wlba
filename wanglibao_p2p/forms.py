# coding=utf-8
from captcha.fields import CaptchaField
import django.forms as forms
from wanglibao_p2p.models import P2PProduct


class PurchaseForm(forms.Form):
    product = forms.ModelChoiceField(queryset=P2PProduct.objects.all(), widget=forms.HiddenInput())
    amount = forms.IntegerField()

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount % 100 != 0:
            raise forms.ValidationError(u'购买金额必须为100的整数倍')
        if amount <= 0:
            raise forms.ValidationError(u'购买金额不能为负数')

        return amount
