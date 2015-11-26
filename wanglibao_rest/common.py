# -*- coding: utf-8 -*-

from rest_framework.views import APIView
from report.crypto import getDecryptedContent
from rest_framework.authentication import get_authorization_header, TokenAuthentication
from django.conf import settings

class DecryptParmsAPIView(APIView):
    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        super(DecryptParmsAPIView, self).initial(request, args, kwargs)
        try:

            method = request.method.lower()
            params = {}
            if method == "get":
                params = request.GET
            if method == "post":
                params = request.DATA
            decrypt_params = params.get("params", None)
            token_key = ""
            if decrypt_params:
                for decrypt_param, length in decrypt_params.iteritems():
                    token_key += decrypt_param
                token_key+=settings.APP_DECRYPT_KEY
                for decrypt_param, length in decrypt_params.iteritems():
                    decrypted = getDecryptedContent(token_key, decrypt_param, length)
                    params[decrypt_param] = decrypted
            print params
        except:
            pass
