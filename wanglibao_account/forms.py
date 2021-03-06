# encoding: utf-8


import json
import logging
import hashlib
from captcha.fields import CaptchaField
from captcha.models import CaptchaStore

from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.db.models import F

from utils import detect_identifier_type, verify_id
from wanglibao_account.models import VerifyCounter, IdVerification, ManualModifyPhoneRecord
from wanglibao_sms.utils import validate_validation_code
from marketing.models import InviteCode, PromotionToken, Channels
from wanglibao_account.utils import mlgb_md5
from marketing.utils import get_channel_record

import time
from hashlib import md5
from rest_framework.authtoken.models import Token
from marketing.models import LoginAccessToken
from django.conf import settings
from wanglibao_profile.models import USER_TYPE
from report.crypto import Aes
from wanglibao_common.tools import StrQuote

User = get_user_model()
logger = logging.getLogger(__name__)


class EmailOrPhoneRegisterForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges
    From a email address or phone number

    phone number will be checked against the validate code, and if passed
    the user will be created and be activated.

    If email address provided, then an activation mail will be sent to the mail
    account is not activated. When the user clicked the activation link, the account
    will be activated.
    """
    # captcha_0 = forms.CharField(label='captcha_0', required=False)
    # captcha_1 = forms.CharField(label='captcha_1', required=False)

    nickname = forms.CharField(label="Nick name", required=False)
    identifier = forms.CharField(label="Email/Phone")
    invitecode = forms.CharField(label="Invitecode", required=False)
    validate_code = forms.CharField(label="Validate code for phone", required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    user_type = forms.CharField(label="User type", required=False)

    MlGb = forms.CharField(label='MlGb', required=False)
    _flag = False

    error_messages = {
        'duplicate_username': u'该邮箱或手机号已经注册',
        'invalid_identifier_type': u'请提供邮箱或者手机号',
        'validate_code_for_email': u'邮箱注册时不需要提供验证码',
        'validate code not match': u'验证码不正确',
        'validate code not exist': u'没有发送验证码',
        'validate must not be null': u'验证码不能为空',
        'invite code not match': u'邀请码错误',
        'mlgb error': u'注册成功',
        'verify_invalid': u'请输入验证码',
        'verify_error': u'短信验证码错误',
        'manual_modify_exists': u'要注册手机号不能为人工修改手机号正在申请修改的手机号',
    }

    class Meta:
        model = get_user_model()
        fields = ("email",)

    #def clean_captcha_1(self):
    #    captcha_1 = self.cleaned_data['captcha_1']
    #    captcha_0 = self.cleaned_data['captcha_0']
    #    if not captcha_0 and not captcha_1:
    #        self._flag = True
    #        return

    #    if not captcha_0 or not captcha_1:
    #        raise forms.ValidationError(
    #            self.error_messages['verify_invalid'],
    #            code='verify_invalid'
    #        )
    #    record = CaptchaStore.objects.filter(hashkey=captcha_0).first()
    #    if not record:
    #        raise forms.ValidationError(
    #            self.error_messages['verify_error'],
    #            code='verify_error'
    #        )
    #    if captcha_1.lower() == record.response.lower():
    #        try:
    #            record.delete()
    #        except:
    #            pass
    #        self._flag = True
    #        return captcha_1.strip()
    #    else:
    #        raise forms.ValidationError(
    #            self.error_messages['verify_error'],
    #            code='verify_error'
    #        )

    def clean_identifier(self):
        """
        since identifier may be a phone number or an email address
        So checking the format here is important
        """

        identifier = self.cleaned_data["identifier"]
        identifier_type = detect_identifier_type(identifier)

        if identifier_type == 'email':
            users = User.objects.filter(email=identifier, is_active=True)
        elif identifier_type == 'phone':
            #users = User.objects.filter(wanglibaouserprofile__phone=identifier, wanglibaouserprofile__phone_verified=True)
            users = User.objects.filter(wanglibaouserprofile__phone=identifier)
        else:
            raise forms.ValidationError(
                self.error_messages['invalid_identifier_type'],
                code='invalid_identifier_type'
            )

        if len(users) == 0:
            manual_modify_exists = ManualModifyPhoneRecord.objects.filter(new_phone=identifier, status__in=[u"待初审", u"初审待定", u"待复审"]).exists()
            if manual_modify_exists:
                raise forms.ValidationError(
                        self.error_messages['manual_modify_exists'],
                        code='manual_modify_exists',
                )
            return identifier.strip()
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username', )

    def clean_invitecode(self):
        invite_code = self.cleaned_data.get('invitecode')

        if invite_code:
            try:
                record = get_channel_record(invite_code)
                if not record:
                    #p = PromotionToken.objects.get(token=invite_code)
                    p = PromotionToken.objects.filter(token=invite_code).first()
                    if not p:
                        raise
            except Exception,e:
                raise forms.ValidationError(
                            self.error_messages['invite code not match'],
                            code='invite code not match',
                        )
            self._flag = True
            return invite_code
        self._flag = True

    def clean_MlGb(self):
        MlGb_src = self.cleaned_data.get('MlGb')

        if MlGb_src:
            try:
                phone = self.cleaned_data.get("identifier")
                if mlgb_md5(phone, 'wang*@li&_!Bao') == MlGb_src:
                    return MlGb_src
            except:
                pass
        """
        raise forms.ValidationError(
                            self.error_messages['mlgb error'],
                            code = 'mlgb error',
                        )
        """

    def clean_validate_code(self):
        if not self._flag:
            return
        if 'identifier' in self.cleaned_data:
            identifier = self.cleaned_data["identifier"]
            identifier_type = detect_identifier_type(identifier)
            if identifier_type == 'phone':
                phone = identifier
                validate_code = self.cleaned_data.get('validate_code', '')
                if validate_code:
                    status, message = validate_validation_code(phone, validate_code)
                    if status != 200:
                        raise forms.ValidationError(
                            # Modify by hb on 2015-12-02
                            #self.error_messages['validate code not match'],
                            message,
                            code='validate_code_error',
                        )
                else:
                    raise forms.ValidationError(
                            self.error_messages['validate must not be null'],
                            code='validate_code_error',
                        )
        return self.cleaned_data

    def clean_user_type(self):
        user_type = self.cleaned_data.get('user_type') or '0'
        if user_type.isdigit():
            if user_type in [i for i, j in USER_TYPE]:
                return user_type

def verify_captcha_enhance(dic, keep=False):
    #add  by yihen@20160525 增强型图片验证码 前端没有传入图片验证的相关信息,不再让其通过; 防刷
    captcha_1 = dic.get('captcha_1', "")
    captcha_0 = dic.get('captcha_0', "")
    if not captcha_0 and not captcha_1:
        return False, u"图片验证码为空"

    if not captcha_0 or not captcha_1:
        return False, u"请输入验证码"
    record = CaptchaStore.objects.filter(hashkey=captcha_0).first()
    if not record:
        return False, u"图片验证码错误"
    # if captcha_1.lower() == record.challenge.lower():
    if captcha_1.lower() == record.response.lower():
        try:
            if not keep: record.delete()
        except:
            pass
        return True, ""
    else:
        return False, u"图片验证码错误"

def verify_captcha(dic, keep=False):
    captcha_1 = dic.get('captcha_1', "")
    captcha_0 = dic.get('captcha_0', "")
    if not captcha_0 and not captcha_1:
        return True, ""

    if not captcha_0 or not captcha_1:
        return False, u"请输入验证码"
    record = CaptchaStore.objects.filter(hashkey=captcha_0).first()
    if not record:
        return False, u"图片验证码错误"
    # if captcha_1.lower() == record.challenge.lower():
    if captcha_1.lower() == record.response.lower():
        try:
            if not keep: record.delete()
        except:
            pass
        return True, ""
    else:
        return False, u"图片验证码错误"


class EmailOrPhoneAuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    identifier = forms.CharField(max_length=254, error_messages={'required': u'请输入手机号'})
    password = forms.CharField(label="Password", widget=forms.PasswordInput, error_messages={'required': u'请输入密码'})
    captcha = CaptchaField(error_messages={'invalid': u'验证码错误', 'required': u'请输入验证码'})

    error_messages = {
        'invalid_login': u"用户名或者密码不正确",
        'frozen': u"用户账户已被冻结",
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(EmailOrPhoneAuthenticationForm, self).__init__(*args, **kwargs)

        self._errors = None

    def clean(self):
        identifier = self.cleaned_data.get('identifier')
        password = self.cleaned_data.get('password')

        if identifier and password:
            self.user_cache = authenticate(identifier=identifier, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'identifier': identifier},
                )
            else:
                if self.user_cache.wanglibaouserprofile.frozen:
                    raise forms.ValidationError(
                        self.error_messages['frozen'],
                        code='frozen',
                        params={'identifier': identifier},
                    )
        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class LoginAuthenticationNoCaptchaForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    identifier = forms.CharField(max_length=254, error_messages={'required': u'请输入手机号'})
    password = forms.CharField(label="Password", widget=forms.PasswordInput, error_messages={'required': u'请输入密码'})

    error_messages = {
        'invalid_login': u"用户名或者密码不正确",
        'frozen': u"用户账户已被冻结",
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(LoginAuthenticationNoCaptchaForm, self).__init__(*args, **kwargs)

        self._errors = None

    def clean(self):
        identifier = self.cleaned_data.get('identifier')
        password = self.cleaned_data.get('password')

        if identifier and password:
            self.user_cache = authenticate(identifier=identifier, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'identifier': identifier},
                )
            else:
                if self.user_cache.wanglibaouserprofile.frozen:
                    raise forms.ValidationError(
                        self.error_messages['frozen'],
                        code='frozen',
                        params={'identifier': identifier},
                    )
        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class ResetPasswordGetIdentifierForm(forms.Form):
    identifier = forms.CharField(max_length=254)


class IdVerificationForm(forms.Form):
    name = forms.CharField(max_length=32, label=u'姓名')
    id_number = forms.CharField(max_length=128, label=u'身份证号')
    # captcha = CaptchaField()

    def __init__(self, user=None, *args, **kwargs):
        super(IdVerificationForm, self).__init__(*args, **kwargs)
        self._user = user


def timestamp():
    return long(time.time())


class TokenSecretSignAuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    token/secret sign logins.
    """
    # token = forms.CharField(max_length=40, error_messages={'required': u'请输入token'})
    # secret_sign = forms.CharField(label="secret_sign", error_messages={'required': u'请输入secret_sign'})
    # ts = forms.CharField(max_length=40, error_messages={'required': u'请输入ts'})

    error_messages = {
        'token_is_null': '1',
        "secret_key_error": '2',
        "secret_key_expired": '3',
        "user_not_exist": '4',
        "user_frozen": '5',
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(TokenSecretSignAuthenticationForm, self).__init__(*args, **kwargs)

        self._errors = None

    def clean(self):
        token_key = self.request.POST.get('token')
        secret_sign = self.request.POST.get('secret_key')
        ts = self.request.POST.get('ts')
        token = None
        if token_key and secret_sign and ts:
            token = Token.objects.get(pk=token_key)

        if not token:
            raise forms.ValidationError(
                self.error_messages["token_is_null"],
                code="token_is_null",
                    )
        user_id = token.user.id
        if secret_sign != md5(str(token.user.id)+settings.WANGLIBAO_ACCESS_TOKEN_KEY+str(ts)).hexdigest():
            raise forms.ValidationError(
                self.error_messages["secret_key_error"],
                code="secret_key_error",
                    )
        loginaccesstoken = LoginAccessToken.objects.filter(token=token).first()
        if loginaccesstoken:
            db_secret_sign = token.loginaccesstoken.secret_sign
            if db_secret_sign == secret_sign:
                now = timestamp()
                if token.loginaccesstoken.expire_at < now:
                    raise forms.ValidationError(
                        self.error_messages["secret_key_expired"],
                        code="secret_key_expired"
                    )
            else:
                token.loginaccesstoken.secret_sign = secret_sign
                token.loginaccesstoken.expire_at = timestamp() + 10 * 60
                token.loginaccesstoken.save()
        else:
            login_access_token = LoginAccessToken()
            login_access_token.secret_sign = secret_sign
            login_access_token.expire_at = timestamp() + 10 * 60
            login_access_token.token = token
            login_access_token.save()

        self.user_cache = authenticate(token=token, secret_sign=secret_sign, ts=ts)
        if self.user_cache is None:
            raise forms.ValidationError(
                self.error_messages["user_not_exist"],
                code="user_not_exist",
            )
        else:
            if self.user_cache.wanglibaouserprofile.frozen:
                raise forms.ValidationError(
                    self.error_messages["user_frozen"],
                    code="user_frozen",
                )
        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache

class ManualModifyPhoneForm(forms.Form):
    error_messages ={
        'validate must not be null': '1',
    }

    id_front_image = forms.ImageField(label='身份证正面照片', required=False)
    id_back_image = forms.ImageField(label='身份证反面照片', required=False)
    id_user_image = forms.ImageField(label='手持身份证照片', required=False)
    card_user_image = forms.ImageField(label='手持银行卡照片', required=False)
    new_phone = forms.CharField(max_length=64, label='新的手机号码')
    validate_code = forms.CharField(label="Validate code for phone", required=False)
    def clean_validate_code(self):
        if 'new_phone' in self.cleaned_data:
            new_phone = self.cleaned_data["new_phone"]
            validate_code = self.cleaned_data.get('validate_code', '')
            if validate_code:
                status, message = validate_validation_code(new_phone, validate_code)
                if status != 200:
                    raise forms.ValidationError(
                        # Modify by hb on 2015-12-02
                        #self.error_messages['validate code not match'],
                        message,
                        code='validate_code_error',
                    )
            else:
                raise forms.ValidationError(
                        self.error_messages['validate must not be null'],
                        code='validate_code_error',
                    )
        return self.cleaned_data


class BiSouYiRegisterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.action = kwargs.pop('action', None)
        super(BiSouYiRegisterForm, self).__init__(*args, **kwargs)

    channel_code = forms.CharField(error_messages={'required': u'渠道码是必须的'})
    client_id = forms.CharField(error_messages={'required': u'客户端id是必须的'})
    sign = forms.CharField(error_messages={'required': u'签名是必须的'})
    content = forms.CharField(error_messages={'required': u'content是必须的'})

    def clean_client_id(self):
        client_id = self.cleaned_data['client_id']
        if client_id == settings.BISOUYI_CLIENT_ID:
            return client_id
        else:
            raise forms.ValidationError(
                code=10012,
                message=u'无效客户端id',
            )

    def clean_channel_code(self):
        channel_code = self.cleaned_data['channel_code']
        if channel_code == 'bisouyi':
            return channel_code
        else:
            raise forms.ValidationError(
                code=10010,
                message=u'无效渠道码',
            )

    def clean_content(self):
        content = self.cleaned_data['content']
        try:
            ase = Aes()
            decrypt_text = ase.decrypt(settings.BISOUYI_AES_KEY, content, mode_tag='ECB')
            content_data = json.loads(decrypt_text)
        except Exception, e:
            logger.info("BiSouYiRegisterForm clean_content raise error: %s" % e)
            raise forms.ValidationError(
                code=10013,
                message=u'content解析失败',
            )
        else:
            if isinstance(content_data, dict):
                if 'mobile' in content_data:
                    phone = str(content_data['mobile'])
                    if detect_identifier_type(phone) == 'phone':
                        if self.action != 'select':
                            users = User.objects.filter(wanglibaouserprofile__phone=phone)
                            if not users.exists() or self.action != 'register':
                                if 'other' in content_data:
                                    if 'account' in content_data:
                                        if self.action == 'login':
                                            if 'token' not in content_data:
                                                raise forms.ValidationError(
                                                    code=10020,
                                                    message=u'content没有包含token'
                                                )
                                        return content, content_data
                                    else:
                                        raise forms.ValidationError(
                                            code=10019,
                                            message=u'content没有包含account'
                                        )
                                else:
                                    raise forms.ValidationError(
                                        code=10018,
                                        message=u'content没有包含other'
                                    )
                            else:
                                raise forms.ValidationError(
                                    code=10017,
                                    message=u'该手机号已被抢注'
                                )
                        else:
                            return content, content_data
                    else:
                        raise forms.ValidationError(
                            code=10014,
                            message=u'无效手机号'
                        )
                else:
                    raise forms.ValidationError(
                        code=10015,
                        message=u'content没有包含phone'
                    )
            else:
                raise forms.ValidationError(
                    code=10016,
                    message=u'content不是期望的类型',
                )

    def get_phone(self):
        phone = str(self.cleaned_data['content'][1]['mobile'])
        return phone

    def get_other(self):
        other = self.cleaned_data['content'][1]['other'] or settings.SITE_URL
        return other

    def get_account(self):
        account = self.cleaned_data['content'][1]['account']
        return account

    def get_token(self):
        token = self.cleaned_data['content'][1]['token']
        return token

    def check_sign(self):
        quote = StrQuote()
        client_id = self.cleaned_data['client_id']
        sign = self.cleaned_data['sign']
        content = self.cleaned_data['content'][0]

        if self.action != 'select':
            content = quote.quote_plus(content)

        local_sign = hashlib.md5(str(client_id) + settings.BISOUYI_CLIENT_SECRET + content).hexdigest()
        if sign != local_sign:
            return False
        else:
            return True
