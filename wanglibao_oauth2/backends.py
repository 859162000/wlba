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
                    return None, None
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
