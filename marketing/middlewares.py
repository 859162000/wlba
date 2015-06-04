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
