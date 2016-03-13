# coding=utf-8

import django.forms as forms
from .models import MarginRecord


class MarginRecordForm(forms.ModelForm):
    catalog = forms.CharField(label=u'流水类型', max_length=100, error_messages={'required': u'请输入流水类型'})
    order_id = forms.IntegerField(label=u'相关订单编号', error_messages={'required': u'请输入相关订单编号'})
    user_id = forms.IntegerField(label=u'用户id', max_length=50, error_messages={'required': u'请输入用户id'})
    create_time = forms.DateTimeField(label=u'流水时间', error_messages={'required': u'请输入流水时间'})
    amount = forms.DecimalField(label=u'发生金额', error_messages={'required': u'请输入发生金额'})
    margin_current = forms.DecimalField(label=u'用户后余额', error_messages={'required': u'请输入用户后余额'})
    description = forms.CharField(label=u'摘要', max_length=1000, error_messages={'required': u'请输入摘要'})

    class Meta:
        model = MarginRecord
