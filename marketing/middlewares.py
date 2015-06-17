# encoding:utf-8
from django.conf import settings
from .models import PromotionToken


class PromotionTokenMiddleWare(object):
    def process_request(self, request):
        token = request.GET.get(settings.PROMO_TOKEN_QUERY_STRING, None)
        product_id = request.GET.get(settings.PROMO_TOKEN_PRODUCT, None)

        if token:
            request.session[settings.PROMO_TOKEN_QUERY_STRING] = token
            request.session[settings.PROMO_TOKEN_PRODUCT] = product_id
            #record = PromotionToken.objects.filter(token=token).first()
            #if record:
            #    request.session[settings.PROMO_TOKEN_USER_SESSION_KEY] = record.pk

        # 易瑞特
        yiruite_from = request.GET.get('from', None)
        yiruite_tid = request.GET.get('tid', 'q823da02cb97f24998f7a5dd44939996')

        if (yiruite_from == settings.YIRUITE_PROMO_TOKEN) and yiruite_tid:
            request.session['yiruite_from'] = yiruite_from
            request.session['yiruite_tid'] = yiruite_tid
