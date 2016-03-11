# encoding: utf-8

from django import forms
from django.contrib.auth import get_user_model
from marketing.utils import get_channel_record

User = get_user_model()


class UserRegisterForm(forms.Form):
    user_id = forms.IntegerField(error_messages={
        'required': u'用户id是必须的',
        'invalid': u'用户id必须是数字'
    })
    phone = forms.IntegerField(error_messages={
        'required': u'用户手机号是必须的',
        'invalid': u'用户手机号必须是数字'
    })
    btype = forms.CharField(error_messages={
        'required': u'用户绑定渠道码是必须的',
    })

    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']
        try:
            User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return user_id
        else:
            raise forms.ValidationError(
                code=10020,
                message=u'用户id已存在'
            )

    def clean_phone(self):
        phone = str(self.cleaned_data['phone'])
        try:
            User.objects.get(wanglibaouserprofile__phone=phone)
        except User.DoesNotExist:
            return phone
        else:
            raise forms.ValidationError(
                code=10021,
                message=u'该手机号已被注册'
            )

    def clean_btype(self):
        btype = self.cleaned_data['btype']
        channel = get_channel_record(btype)
        if channel:
            return channel
        else:
            raise forms.ValidationError(
                code=10022,
                message=u'无效用户绑定渠道码'
            )


class UserForm(forms.Form):
    user_id = forms.IntegerField(error_messages={
        'required': u'用户id是必须的',
        'invalid': u'用户id必须是数字'
    })

    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise forms.ValidationError(
                code=10020,
                message=u'无效用户id'
            )
        else:
            return user
