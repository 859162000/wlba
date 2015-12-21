from django import forms
from django.contrib.auth import authenticate

class OpenidAuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    token/secret sign logins.
    """

    error_messages = {
        'param_is_null': '1',
        'user_not_exist': '2',
    }

    def __init__(self, openid, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """

        self.openid = openid
        self.user_cache = None
        super(OpenidAuthenticationForm, self).__init__(*args, **kwargs)

        self._errors = None

    def clean(self):
        print 'self.openid==%s'%self.openid
        self.user_cache = authenticate(openid=self.openid)
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

    def get_user(self):
        return self.user_cache
