# encoding:utf-8

from django.conf import settings
from wanglibao_account.cooperation import CoopLandProcessor


class PromotionTokenMiddleWare(object):
    def process_request(self, request):
        token = request.GET.get(settings.PROMO_TOKEN_QUERY_STRING, None)
        if token:
            # URI == LAND_URI_FOR_CHANNEL 无需保存session
            # if request.path != settings.LAND_URI_FOR_CHANNEL:
                # request.session[settings.PROMO_TOKEN_QUERY_STRING] = token
            CoopLandProcessor(request).process_for_session(0)

    def process_response(self, request, response):
        token = request.GET.get(settings.PROMO_TOKEN_QUERY_STRING, None)
        if token:
            CoopLandProcessor(request).process_for_session(1)

        return response
