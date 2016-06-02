# encoding:utf-8

from django.conf import settings
from wanglibao_account.cooperation import CoopLandProcessor


class PromotionTokenMiddleWare(object):
    def process_request(self, request):
        token = request.GET.get(settings.PROMO_TOKEN_QUERY_STRING, None)
        if token:
            request.session[settings.PROMO_TOKEN_QUERY_STRING] = token
            CoopLandProcessor(request).all_processors_for_session(0)
