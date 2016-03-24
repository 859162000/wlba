# encoding:utf-8

from django import forms
from wanglibao_profile.models import WanglibaoUserProfile, ActivityUserInfo


class ActivityUserInfoForm(forms.ModelForm):
    phone = forms.CharField(label=u'手机号', error_messages={'required': u'请输入手机号'})
    name = forms.CharField(label=u'姓名', error_messages={'required': u'请输入姓名'})
    address = forms.CharField(label=u'地址', error_messages={'required': u'请输入地址'})

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()

        if len(phone) == 11:
            user_infos = ActivityUserInfo.objects.filter(phone=phone)
            if user_infos.exists():
                raise forms.ValidationError(
                    code=10003,
                    message=u'该手机号已经上报过')
            else:
                return phone
        else:
            raise forms.ValidationError(
                code=10002,
                message=u'无效手机号',
            )

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        return name

    def clean_address(self):
        address = self.cleaned_data['address'].strip()
        return address

    def check_wlb_phone(self):
        phone = self.cleaned_data['phone']

        profile_phones = WanglibaoUserProfile.objects.filter(phone=phone)
        if profile_phones.exists():
            return 1
        else:
            return 0

    class Meta:
        model = ActivityUserInfo
