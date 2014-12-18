# encoding: utf-8
from captcha.fields import CaptchaField

from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.db.models import F

from utils import detect_identifier_type, verify_id
from wanglibao_account.models import VerifyCounter, IdVerification
from wanglibao_sms.utils import validate_validation_code
from marketing.models import InviteCode, PromotionToken
from wanglibao_account.utils import mlgb_md5

User = get_user_model()


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
    nickname = forms.CharField(label="Nick name", required=False)
    identifier = forms.CharField(label="Email/Phone")
    validate_code = forms.CharField(label="Validate code for phone", required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    invitecode = forms.CharField(label="Invitecode", required=False)

    MlGb = forms.CharField(label='MlGb', required=False)

    error_messages = {
        'duplicate_username': u'该邮箱或手机号已经注册',
        'invalid_identifier_type': u'请提供邮箱或者手机号',
        'validate_code_for_email': u'邮箱注册时不需要提供验证码',
        'validate code not match': u'验证码不正确',
        'validate code not exist': u'没有发送验证码',
        'validate must not be null': u'验证码不能为空',
        'invite code not match': u'邀请码错误',
        'mlgb error': u'注册成功'
    }

    class Meta:
        model = get_user_model()
        fields = ("email",)

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
            users = User.objects.filter(wanglibaouserprofile__phone=identifier, wanglibaouserprofile__phone_verified=True)
        else:
            raise forms.ValidationError(
                self.error_messages['invalid_identifier_type'],
                code='invalid_identifier_type'
            )

        if len(users) == 0:
            return identifier.strip()
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username', )

    def clean_invitecode(self):
        invite_code = self.cleaned_data.get('invitecode')

        if invite_code:
            try:
                p = PromotionToken.objects.get(token=invite_code)
            except:
                raise forms.ValidationError(
                            self.error_messages['invite code not match'],
                            code='invite code not match',
                        )
            return invite_code

    def clean_MlGb(self):
        MlGb_src = self.cleaned_data.get('MlGb')

        if MlGb_src:
            phone = self.cleaned_data.get("identifier")
            if mlgb_md5(phone, 'wang*@li&_!Bao') == MlGb_src:
                return MlGb_src

        raise forms.ValidationError(
                            self.error_messages['mlgb error'],
                            code = 'mlgb error',
                        )

    def clean_validate_code(self):
        if 'identifier' in self.cleaned_data:
            identifier = self.cleaned_data["identifier"]
            identifier_type = detect_identifier_type(identifier)
            if identifier_type == 'phone':
                phone = identifier
                validate_code =  self.cleaned_data.get('validate_code', '')
                if validate_code:
                    status, message = validate_validation_code(phone, validate_code)
                    if status != 200:
                        raise forms.ValidationError(
                            self.error_messages['validate code not match'],
                            code='validate_code_error',
                        )
                else:
                    raise forms.ValidationError(
                            self.error_messages['validate must not be null'],
                            code='validate_code_error',
                        )
        return self.cleaned_data




class EmailOrPhoneAuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    identifier = forms.CharField(max_length=254)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    captcha = CaptchaField()

    error_messages = {
        'invalid_login': u"用户名或者密码不正确",
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

