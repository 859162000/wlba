# encoding: utf-8

from django import forms
from wanglibao_p2p.models import P2PProduct


class FuelCardBuyForm(forms.ModelForm):
    """
    加油卡购买参数验证表单
    """

    p_id = forms.IntegerField(required=True)
    p_parts = forms.IntegerField(required=True)
    total_amount = forms.FloatField(required=True)
    using_range = forms.CharField(required=True)

    def clean_p_id(self):
        p_id = self.cleaned_data['p_id'].strip()
        try:
            p2p_product = P2PProduct.objects.get(pk=p_id)
        except P2PProduct.DoesNotExist:
            raise forms.ValidationError(
                self.error_messages['invalid product id'],
                code=10001
            )

        self.cleaned_data['p2p_product'] = p2p_product

        return p_id

    def clean_p_parts(self):
        return self.cleaned_data['p_parts'].strip()

    def clean_total_amount(self):
        return self.cleaned_data['total_amount'].strip()

    def clean_using_range(self):
        return self.cleaned_data['using_range'].strip()
