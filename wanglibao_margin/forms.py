# coding=utf-8

import django.forms as forms
from .models import Margin, MarginRecord


class MarginForm(forms.ModelForm):
    margin = forms.CharField(label=u'用户余额', error_messages={'required': u'请输入用户余额'})
    freeze = forms.CharField(label=u'冻结金额', error_messages={'required': u'请输入冻结金额'})
    withdrawing = forms.CharField(label=u'提款中金额', error_messages={'required': u'请输入提款中金额'})
    invest = forms.CharField(label=u'已投资金额', error_messages={'required': u'请输入已投资金额'})
    uninvested = forms.CharField(label=u'充值未投资金额', error_messages={'required': u'请输入充值未投资金额'})
    uninvested_freeze = forms.CharField(label=u'充值未投资冻结金额', error_messages={'required': u'请输入充值未投资冻结金额'})

    class Meta:
        model = Margin


class MarginRecordForm(forms.ModelForm):
    catalog = forms.CharField(label=u'流水类型', error_messages={'required': u'请输入流水类型'})
    order_id = forms.IntegerField(label=u'相关订单编号', error_messages={'required': u'请输入相关订单编号'})
    user_id = forms.IntegerField(label=u'用户id', error_messages={'required': u'请输入用户id'})
    create_time = forms.DateTimeField(label=u'流水时间', error_messages={'required': u'请输入流水时间'})
    amount = forms.DecimalField(label=u'发生金额', error_messages={'required': u'请输入发生金额'})
    margin_current = forms.DecimalField(label=u'用户后余额', error_messages={'required': u'请输入用户后余额'})
    description = forms.CharField(label=u'摘要', required=False, error_messages={'required': u'请输入摘要'})

    class Meta:
        model = MarginRecord
