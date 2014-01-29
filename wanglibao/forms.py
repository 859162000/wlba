from django import forms
from django.contrib.auth import get_user_model, authenticate
from wanglibao_profile.models import PhoneValidateCode, WanglibaoUserProfile

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
    username = forms.CharField(label="Username", required=False)
    identifier = forms.CharField(label="Email/Phone")
    validate_code = forms.CharField(label="Validate code for phone", required=False)
    type = forms.CharField(initial="email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    error_messages = {
        'duplicate_email': 'The email is already registered',
        'duplicate_phone': 'The phone number already registered'
    }

    class Meta:
        model = get_user_model()
        fields = ("username", "email")

    def clean_identifier(self):
        """
        since identifier may be a phone number or an email address
        So checking the format here is important
        """

        identifier = self.cleaned_data["identifier"]
        identifier_type = self.clean_type()

        users = None
        if identifier_type == 'email':
            users = User.objects.filter(email=identifier, is_active=True)
        elif identifier_type == 'phone':
            users = User.objects.filter(wanglibaouserprofile__phone=identifier, is_active=True)

        if len(users) == 0:
            return identifier.strip()
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username', )

    def clean_type(self):
        identifier_type = self.data["type"]
        if identifier_type not in ['email', 'phone']:
            raise forms.ValidationError(
                self.error_messages['type_invalid'],
                code='type_invalid',)
        return identifier_type

    def clean_validate_code(self):
        validate_code = self.cleaned_data["validate_code"]
        if self.clean_type() == 'phone':
            # phone = self.cleaned_data["identifier"]
            phone = self.clean_identifier()
            try:
                phone_validate = PhoneValidateCode.objects.get(phone=phone)
                # TODO Check the validate_code period, 30 minutes
                if phone_validate.validate_code == validate_code:
                    return validate_code
                else:
                    raise forms.ValidationError(
                        self.error_messages['validate code not match'],
                        code='validate_code_error',
                    )
            except PhoneValidateCode.DoesNotExist, e:
                raise forms.ValidationError(
                    self.error_messages['validate code not exist'],
                    code='validate_code_error',
                )
        return validate_code

class EmailOrPhoneAuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    identifier = forms.CharField(max_length=254)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': "Please enter a correct %(username)s and password. "
                           "Note that both fields may be case-sensitive.",
        'inactive': "This account is inactive.",
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(EmailOrPhoneAuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        identifier = self.cleaned_data.get('identifier')
        password = self.cleaned_data.get('password')

        if identifier and password:
            self.user_cache = authenticate(identifier=identifier, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache