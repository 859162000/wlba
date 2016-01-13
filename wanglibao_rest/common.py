# -*- coding: utf-8 -*-

from rest_framework.views import APIView
from report.crypto import getDecryptedContent
from rest_framework.authentication import get_authorization_header, TokenAuthentication
from django.conf import settings
import json
import logging

logger = logging.getLogger("wanglibao_rest")

class DecryptParmsAPIView(APIView):
    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        super(DecryptParmsAPIView, self).initial(request, args, kwargs)
        try:
            # logger.debug("===decrypt in wanglibao_rest.common====request_params:%s"%request.__dict__)
            method = request.method.lower()
            self.params = {}
            request_params = {}
            if method == "get":
                request_params = request.GET
            if method == "post":
                request_params = request.DATA

            token_key = ""
            for k, v in request_params.iteritems():
                if k == 'param':
                    self.params[k] = {}
                    if type(v) is unicode:
                        p_v = json.loads(v)
                        for vk, vv in p_v.iteritems():
                            token_key += vk
                            self.params[k][vk] = vv
                    elif type(v) is dict:
                        for vk, vv in v.iteritems():
                            token_key += vk
                            self.params[k][vk] = vv
                    if token_key:
                        token_key = "".join(sorted(list(token_key)))
                        token_key += settings.APP_DECRYPT_KEY
                else:
                    self.params[k] = v
            if self.params.get("param", {}):
                for key, length in self.params.get("param", {}).iteritems():
                    content = self.params.get(key, "")
                    self.params[key] = getDecryptedContent(token_key, content, int(length))
        except Exception, e:
            logger.debug("===decrypt in wanglibao_rest.common====error:%s"%e.message)

