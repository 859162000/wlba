# encoding:utf-8

import re
from django import forms
from wanglibao_profile.models import WanglibaoUserProfile, ActivityUserInfo


class ActivityUserInfoForm(forms.ModelForm):
    phone = forms.IntegerField(label=u'手机号', error_messages={'required': u'请输入手机号'})
    name = forms.CharField(label=u'姓名', error_messages={'required': u'请输入姓名'})
    address = forms.CharField(label=u'地址', error_messages={'required': u'请输入地址'})

    def get_unicode_len(self, unicode_content):
        unicode_str_len = len(unicode_content)
        re_words = re.compile(u"[\u4e00-\u9fa5]+")
        m = re_words.search(unicode_content, 0)

        if m:
            zh_str_len = len(m.group())
            en_str_len = unicode_str_len - zh_str_len
            name_len = en_str_len + (zh_str_len * 2)
        else:
            name_len = unicode_str_len

        return name_len

    def clean_phone(self):
        phone = self.cleaned_data['phone']

        if len(str(phone)) == 11:
            user_infos = ActivityUserInfo.objects.filter(phone=phone)
            if user_infos.exists():
                raise forms.ValidationError(
                    code=10003,
                    message=u'请勿重复上报')
            else:
                return phone
        else:
            raise forms.ValidationError(
                code=10002,
                message=u'无效手机号',
            )

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        name_len = self.get_unicode_len(name)

        if name_len <= 20:
            return name
        else:
            raise forms.ValidationError(
                code=10003,
                message=u'长度超出限制',
            )

    def clean_address(self):
        address = self.cleaned_data['address'].strip()
        address_len = self.get_unicode_len(address)

        if address_len <= 20:
            return address
        else:
            raise forms.ValidationError(
                code=10003,
                message=u'长度超出限制',
            )

    def check_wlb_phone(self):
        phone = self.cleaned_data['phone']

        profile_phones = WanglibaoUserProfile.objects.filter(phone=phone)
        if profile_phones.exists():
            return 1
        else:
            return 0

    class Meta:
        model = ActivityUserInfo
