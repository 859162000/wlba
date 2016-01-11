# encoding: utf-8

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.tokens import default_token_generator

from .forms import ClientAuthForm
from .models import AccessToken
from .utils import now


class BasicClientBackend(object):
    def authenticate(self, request=None):
        error_data = None
        client_id = request.POST.get('client_id', '').strip()
        if client_id:
            try:
                form = ClientAuthForm(request.POST)
                if form.is_valid():
                    return form.cleaned_data['client'], error_data
                else:
                    print ">>>>>>>>>>>>>", form.errors
                    form_errors = form.errors
                    form_error_keys = form_errors.keys()
                    form_errors_list = []
                    for key in form_error_keys:
                        value = form_errors[key]
                        form_error = u'、'.join(value)
                        form_errors_list.append(form_error)

                        response_data = {
                            'message': u'表单错误：' + u'、'.join(form_errors_list),
                            'ret_code': 10001,
                        }
            except ValueError:
                # Auth header was malformed, unpacking went wrong
                return None, None


class AccessTokenBackend(ModelBackend):
    """
    Authenticate a user via access token and client object.
    """

    def authenticate(self, token, client_id, user_id):
        try:
            user = AccessToken.objects.get(token=token,
                                           expires__gt=now(),
                                           client__client_id=client_id,
                                           user_id=user_id).user
        except AccessToken.DoesNotExist:
            return None

        if default_token_generator.check_token(user, token):
            return user

        return None
