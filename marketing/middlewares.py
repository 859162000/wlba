# encoding:utf-8
from django.conf import settings
from .models import PromotionToken
from wanglibao_account.cooperation import CoopRegister
from rest_framework.authtoken.models import Token
from marketing.models import LoginAccessToken
import json
from django.http.response import HttpResponse
import time

def timestamp():
    return long(time.time())

class PromotionTokenMiddleWare(object):
    def process_request(self, request):
        token = request.GET.get(settings.PROMO_TOKEN_QUERY_STRING, None)
        if token:
            request.session[settings.PROMO_TOKEN_QUERY_STRING] = token
        CoopRegister(request).all_processors_for_session()

class LoginAccessTokenMiddleWare(object):
    def process_request(self, request):

        access_token = request.GET.get('ACCESS_TOKEN_QUERY_STRING', None)
        params = request.GET
        if not access_token:
            access_token = request.POST.get('ACCESS_TOKEN_QUERY_STRING', None)
            params = request.POST
        if access_token:
            token_key = params.get('token', None)
            token = Token.objects.get(pk=token_key)
            if not token:
                json_response = {
                    'ret_code': -1,
                    'message': u'token error！！！'
                     }
                return HttpResponse(json.dumps(json_response), content_type='application/json')
            if token:
                a_token = LoginAccessToken.objects.filter(token=token)
                if a_token.exists():
                    if a_token.access_token == access_token:
                        if a_token.update_at + 10*60 >= timestamp():
                            request.session['ACCESS_TOKEN_UID'] = token.user.id
                        else:
                            json_response = {
                                'ret_code': -1,
                                'message': u'access_token expired！！！'
                                 }
                            return HttpResponse(json.dumps(json_response), content_type='application/json')
                    else:
                        pass

                # request.session['ACCESS_TOKEN_QUERY_STRING'] = access_token


    def process_response(self, request, response):
        pass

    def check_expire(self):
        pass


