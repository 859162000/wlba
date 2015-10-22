from .forms import ClientAuthForm
from .models import AccessToken
from .utils import now


class BasicClientBackend(object):
    def authenticate(self, request=None):
        client_id = request.POST.get('appid').strip()
        signature = request.POST.get('signature').strip()
        usn = request.POST.get('usn').strip()

        if client_id:
            try:
                form = ClientAuthForm({
                    'client_id': client_id,
                    'signature': signature,
                    'usn': usn,
                    })
                if form.is_valid():
                    return form.cleaned_data.get('client')
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
                expires__gt=now(), client=client)
        except AccessToken.DoesNotExist:
            return None
