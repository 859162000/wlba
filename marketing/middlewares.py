# encoding:utf-8
from django.conf import settings
from .models import PromotionToken


class PromotionTokenMiddleWare(object):
    def process_request(self, request):
        token = request.GET.get(settings.PROMO_TOKEN_QUERY_STRING, None)
        #product_id = request.GET.get(settings.PROMO_TOKEN_PRODUCT, None)

        # 天芒云
        tianmang_source = request.GET.get('source', None)
        tianmang_sn = request.GET.get('sn', None)

        # 易瑞特
        yiruite_from = request.GET.get('from', None)
        yiruite_tid = request.GET.get('tid', 'q823da02cb97f24998f7a5dd44939996')

        if token:
            request.session[settings.PROMO_TOKEN_QUERY_STRING] = token
            #request.session[settings.PROMO_TOKEN_PRODUCT] = product_id
        elif (tianmang_source == 'tianmang') and tianmang_sn:
            request.session['tianmang_source'] = tianmang_source
            request.session['tianmang_sn'] = tianmang_sn
        elif yiruite_from and yiruite_tid:
            # request.session['yiruite_from'] = yiruite_from
            request.session[settings.PROMO_TOKEN_QUERY_STRING] = yiruite_from
            request.session['yiruite_tid'] = yiruite_tid
        else:
            pass
