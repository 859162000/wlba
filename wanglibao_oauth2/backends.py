# encoding: utf-8

import logging
from .forms import ClientAuthForm

logger = logging.getLogger(__name__)


class BasicClientBackend(object):
    def authenticate(self, request=None):
        client = None
        error_data = None
        client_id = request.POST.get('client_id', '').strip()
        if not client_id:
            client_id = request.session.get('client_id', '').strip()

        if client_id:
            form = ClientAuthForm({'client_id': client_id})
            if form.is_valid():
                client = form.cleaned_data['client']
            else:
                error_data = form.errors

        return client, error_data
