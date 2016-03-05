# encoding:utf-8

from django import forms


class ChannelForm(forms.Form):
    channel_code = forms.CharField(error_messages={
        'required': u'渠道码是必须的',
    })
    channel_name = forms.CharField(error_messages={
        'required': u'渠道名是必须的',
    })
