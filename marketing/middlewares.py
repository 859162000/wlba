# encoding:utf-8
from django.conf import settings
from .models import PromotionToken


class PromotionTokenMiddleWare(object):
    def process_request(self, request):
        token = request.GET.get(settings.PROMO_TOKEN_QUERY_STRING, None)
        #product_id = request.GET.get(settings.PROMO_TOKEN_PRODUCT, None)

        if token:
            request.session[settings.PROMO_TOKEN_QUERY_STRING] = token
            #request.session[settings.PROMO_TOKEN_PRODUCT] = product_id

        """
        # 天芒云
        tianmang_source = request.GET.get('source', None)
        tianmang_sn = request.GET.get('sn', None)

        # 易瑞特
        # yiruite_from = request.GET.get('from', None)
        yiruite_tid = request.GET.get('tid', 'q823da02cb97f24998f7a5dd44939996')

        if token and not yiruite_tid:
            request.session[settings.PROMO_TOKEN_QUERY_STRING] = token
            request.session[settings.PROMO_TOKEN_PRODUCT] = product_id
            #record = PromotionToken.objects.filter(token=token).first()
            #if record:
            #    request.session[settings.PROMO_TOKEN_USER_SESSION_KEY] = record.pk
        elif (tianmang_source == 'tianmang') and tianmang_sn:
            request.session['tianmang_source'] = tianmang_source
            request.session['tianmang_sn'] = tianmang_sn
        elif (token == 'yiruite') and yiruite_tid:
            # request.session['yiruite_from'] = yiruite_from
            request.session[settings.PROMO_TOKEN_QUERY_STRING] = token
            request.session['yiruite_tid'] = yiruite_tid
        else:
            pass
        """
