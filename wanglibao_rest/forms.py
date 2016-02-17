# encoding:utf-8

from django import forms
from marketing.utils import get_channel_record


class CoopDataDispatchForm(forms.Form):
    channel_code = forms.CharField()
    sign = forms.CharField()
    act = forms.CharField()

    def clean_channel_code(self):
        channel_code = self.cleaned_data['channel_code']
        if get_channel_record(channel_code):
            return channel_code
        else:
            raise forms.ValidationError(u'无效channel_code')

    def clean_act(self):
        pass

