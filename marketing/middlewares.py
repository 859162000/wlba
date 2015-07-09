# encoding:utf-8
from django.conf import settings
from .models import PromotionToken
from wanglibao_account.cooperation import CoopRegister


class PromotionTokenMiddleWare(object):
    def process_request(self, request):
        token = request.GET.get(settings.PROMO_TOKEN_QUERY_STRING, None)
        if token:
            request.session[settings.PROMO_TOKEN_QUERY_STRING] = token
        CoopRegister(request).all_processors_for_session()
