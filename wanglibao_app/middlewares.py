# encoding:utf-8
from django.conf import settings
from rest_framework import exceptions, HTTP_HEADER_ENCODING



class DisableAppCsrfCheck(object):
    def process_request(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != b'token':
            return None
        if not hasattr(request, '_dont_enforce_csrf_checks'):
            setattr(request, '_dont_enforce_csrf_checks', True)


def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if type(auth) == type(''):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth

