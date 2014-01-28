from django import forms
from django.contrib.auth import get_user_model
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
    username = forms.CharField(label="Username")
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

        if identifier_type == 'email':
            users = User.objects.filter(email=identifier, is_active=True)
            if len(users) == 0:
                return identifier
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
            phone = self.cleaned_data.get("phone")
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

    def save(self, commit=True):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        user = User.objects.create(username=username)
        user.set_password(password)

        identifier = self.cleaned_data('identifier')
        identifier_type = self.clearned_data('type')
        if identifier_type == 'email':
            user.email = identifier
            user.is_active = False
            # TODO Trigger send activation mail by utilizing registration library

        elif identifier_type == 'phone':
            profile = WanglibaoUserProfile.objects.create()
            profile.phone = identifier
            profile.phone_verified = True
            profile.save()
            user.wanglibaouserprofile = profile

        if commit:
            user.save()
        return user
