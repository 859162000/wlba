# encoding: utf-8

from common import forms
from django.contrib.auth import get_user_model
from common.forms import ValidationError, Form
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


class UserValidateForm(Form):
    name = forms.CharField(max_length=32, label=u'姓名', error_messages={'required': u'姓名是必须的'})
    id_number = forms.CharField(max_length=128, label=u'身份证号', error_messages={'required': u'身份证号是必须的'})
    id_valid_time = forms.CharField(max_length=30, label=u'实名时间', error_messages={'required': u'实名时间是必须的'})
    user_id = forms.IntegerField(error_messages={
        'required': u'用户id是必须的',
        'invalid': u'用户id必须是数字'
    })

    def clean_id_number(self):
        raise ValidationError(
            code=10030,
            message=u'无效id_number'
        )

        return id_number

    def clean_user_id(self):
        raise ValidationError(
            code=10020,
            message=u'无效用户id'
        )
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


# class BiSouYiRegisterForm(forms.Form):
#     def __init__(self, *args, **kwargs):
#         self.action = kwargs.pop('action', None)
#         super(BiSouYiRegisterForm, self).__init__(*args, **kwargs)
#
#     channel_code = forms.CharField(error_messages={'required': u'渠道码是必须的'})
#     client_id = forms.CharField(error_messages={'required': u'客户端id是必须的'})
#     sign = forms.CharField(error_messages={'required': u'签名是必须的'})
#     content = forms.CharField(error_messages={'required': u'content是必须的'})
#
#     def clean_client_id(self):
#         client_id = self.cleaned_data['client_id']
#         if client_id == settings.BISOUYI_CLIENT_ID:
#             return client_id
#         else:
#             raise forms.ValidationError(
#                 code=10012,
#                 message=u'无效客户端id',
#             )
#
#     def clean_channel_code(self):
#         channel_code = self.cleaned_data['channel_code']
#         if channel_code == 'bisouyi':
#             return channel_code
#         else:
#             raise forms.ValidationError(
#                 code=10010,
#                 message=u'无效渠道码',
#             )
#
#     def clean_content(self):
#         content = self.cleaned_data['content']
#         try:
#             ase = Aes()
#             decrypt_text = ase.decrypt(settings.BISOUYI_AES_KEY, content, mode_tag='ECB')
#             content_data = json.loads(decrypt_text)
#         except Exception, e:
#             logger.info("BiSouYiRegisterForm clean_content raise error: %s" % e)
#             raise forms.ValidationError(error_dict
#                 code=10013,
#                 message=u'content解析失败',
#             )
#         else:
#             if isinstance(content_data, dict):
#                 if 'mobile' in content_data:
#                     phone = str(content_data['mobile'])
#                     if detect_identifier_type(phone) == 'phone':
#                         if self.action != 'select':
#                             users = User.objects.filter(wanglibaouserprofile__phone=phone)
#                             if not users.exists() or self.action != 'register':
#                                 if 'other' in content_data:
#                                     if 'account' in content_data:
#                                         if self.action == 'login':
#                                             if 'token' not in content_data:
#                                                 raise forms.ValidationError(
#                                                     code=10020,
#                                                     message=u'content没有包含token'
#                                                 )
#                                         return content, content_data
#                                     else:
#                                         raise forms.ValidationError(
#                                             code=10019,
#                                             message=u'content没有包含account'
#                                         )
#                                 else:
#                                     raise forms.ValidationError(
#                                         code=10018,
#                                         message=u'content没有包含other'
#                                     )
#                             else:
#                                 raise forms.ValidationError(
#                                     code=10017,
#                                     message=u'该手机号已被抢注'
#                                 )
#                         else:
#                             return content, content_data
#                     else:
#                         raise forms.ValidationError(
#                             code=10014,
#                             message=u'无效手机号'
#                         )
#                 else:
#                     raise forms.ValidationError(
#                         code=10015,
#                         message=u'content没有包含phone'
#                     )
#             else:
#                 raise forms.ValidationError(
#                     code=10016,
#                     message=u'content不是期望的类型',
#                 )
#
#     def get_phone(self):
#         phone = str(self.cleaned_data['content'][1]['mobile'])
#         return phone
#
#     def get_other(self):
#         other = self.cleaned_data['content'][1]['other'] or settings.SITE_URL
#         return other
#
#     def get_account(self):
#         account = self.cleaned_data['content'][1]['account']
#         return account
#
#     def get_token(self):
#         token = self.cleaned_data['content'][1]['token']
#         return token
#
#     def check_sign(self):
#         quote = StrQuote()
#         client_id = self.cleaned_data['client_id']
#         sign = self.cleaned_data['sign']
#         content = self.cleaned_data['content'][0]
#
#         if self.action != 'select':
#             content = quote.quote_plus(content)
#
#         local_sign = hashlib.md5(str(client_id) + settings.BISOUYI_CLIENT_SECRET + content).hexdigest()
#         if sign != local_sign:
#             return False
#         else:
#             return True

