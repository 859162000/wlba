# encoding: utf-8
from captcha.fields import CaptchaField

from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError

from utils import detect_identifier_type, verify_id
from wanglibao_sms.utils import validate_validation_code

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
    nickname = forms.CharField(label="Nick name", required=True)
    identifier = forms.CharField(label="Email/Phone")
    validate_code = forms.CharField(label="Validate code for phone", required=False)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    error_messages = {
        'duplicate_username': u'该邮箱或手机号已经注册',
        'invalid_identifier_type': u'请提供邮箱或者手机号',
        'validate_code_for_email': u'邮箱注册时不需要提供验证码',
        'validate code not match': u'验证码不正确',
        'validate code not exist': u'没有发送验证码'
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

    def clean(self):
        validate_code = self.cleaned_data["validate_code"]
        if 'identifier' in self.cleaned_data:
            identifier = self.cleaned_data["identifier"]
            identifier_type = detect_identifier_type(identifier)
            if identifier_type == 'phone':
                phone = identifier
                status, message = validate_validation_code(phone, validate_code)
                if status != 200:
                    raise forms.ValidationError(
                        self.error_messages['validate code not match'],
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

    def clean(self):
        cleaned_data = super(IdVerificationForm, self).clean()

        name = cleaned_data.get('name')
        id_number = cleaned_data.get('id_number')
        verify_record, error = verify_id(name, id_number)

        if not verify_record.is_valid:
            raise ValidationError(u'验证失败，拨打客服电话进行人工验证')

        return cleaned_data
