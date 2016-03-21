# coding=utf-8
import django.forms as forms
from django.contrib.auth.models import User
from django.utils import timezone
from wanglibao_p2p.models import P2PProduct, UserAmortization, P2PRecord


class PurchaseForm(forms.Form):
    catalog = forms.CharField(error_messages={
        'required': u'catalog是必须的',
    })
    order_id = forms.IntegerField(error_messages={
        'required': u'订单号是必须的',
        'invalid': u'订单号必须是数字'
    })
    amount = forms.IntegerField(error_messages={
        'required': u'投资金额是必须的',
        'invalid': u'投资金额必须是数字'
    })
    product_id = forms.IntegerField(error_messages={
        'required': u'产品id是必须的',
        'invalid': u'产品id必须是数字'
    })
    user_id = forms.IntegerField(error_messages={
        'required': u'用户id是必须的',
        'invalid': u'用户id必须是数字'
    })
    purchase_at = forms.IntegerField(error_messages={
        'required': u'投资时间是必须的',
        'invalid': u'投资时间必须是数字'
    })

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount % 100 != 0 or amount <= 0:
            raise forms.ValidationError(
                code=10041,
                message=u'无效投资金额',
            )

        return amount

    def clean_product_id(self):
        product_id = self.cleaned_data['product_id']
        try:
            product = P2PProduct.objects.get(pk=product_id)
        except P2PProduct.DoesNotExist:
            raise forms.ValidationError(
                code=10042,
                message=u'无效产品id',
            )

        return product

    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise forms.ValidationError(
                code=10043,
                message=u'无效用户id',
            )

        return user

    def clean_purchase_at(self):
        purchase_at = self.cleaned_data['purchase_at']
        if len(str(purchase_at)) == 13:
            purchase_at = timezone.localtime(purchase_at)
        else:
            raise forms.ValidationError(
                code=10044,
                message=u'无效投资时间',
            )

        return purchase_at


class P2PProductForm(forms.ModelForm):
    class Meta:
        model = P2PProduct


class UserAmortizationForm(forms.ModelForm):
    class Meta:
        model = UserAmortization


class P2PRecordForm(forms.ModelForm):
    catalog = forms.CharField(label=u'流水类型', error_messages={'required': u'请输入流水类型'})
    order_id = forms.IntegerField(label=u'关联订单编号', error_messages={'required': u'请输入关联订单编号'})
    amount = forms.DecimalField(label=u'发生数', error_messages={'required': u'请输入发生数'})
    product_balance_after = forms.IntegerField(label=u'标的后余额', error_messages={'required': u'请输入标的后余额'})
    create_time = forms.DateTimeField(label=u'发生时间', error_messages={'required': u'请输入发生时间'})
    description = forms.CharField(label=u'摘要', required=False, error_messages={'required': u'请输入摘要'})
    platform = forms.CharField(label=u'购买平台', required=False, error_messages={'required': u'请输入购买平台'})

    class Meta:
        model = P2PRecord
