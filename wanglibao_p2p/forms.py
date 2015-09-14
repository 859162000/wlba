# coding=utf-8
from captcha.fields import CaptchaField
import django.forms as forms
from django.forms.models import BaseInlineFormSet
from wanglibao_p2p.models import P2PProduct
from ckeditor.widgets import CKEditorWidget


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
        'required': u'购买金额不能为空',
        'invalid': u'请输入整数'
    })

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError(u'购买金额不能为负数')

        return amount


class RequiredInlineFormSet(BaseInlineFormSet):
    """
    Generates an inline formset that is required
    """

    def _construct_form(self, i, **kwargs):
        """
        Override the method to change the form attribute empty_permitted
        """
        form = super(RequiredInlineFormSet, self)._construct_form(i, **kwargs)
        form.empty_permitted = False
        return form



class ContractTemplateForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(config_name="mini"))
    content_preview = forms.CharField(widget=CKEditorWidget(config_name="mini"))