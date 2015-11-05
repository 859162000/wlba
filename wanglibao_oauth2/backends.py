from .forms import ClientAuthForm
from .models import AccessToken
from .utils import now


class BasicClientBackend(object):
    def authenticate(self, request=None):
        client_id = request.POST.get('client_id', '').strip()
        if client_id:
            try:
                form = ClientAuthForm(request.POST)
                if form.is_valid():
                    return form.cleaned_data['client']
                return None

            except ValueError:
                # Auth header was malformed, unpacking went wrong
                return None


class AccessTokenBackend(object):
    """
    Authenticate a user via access token and client object.
    """

    def authenticate(self, access_token=None, client=None):
        try:
            return AccessToken.objects.get(token=access_token,
                                           expires__gt=now(),
                                           client=client)
        except AccessToken.DoesNotExist:
            return None
