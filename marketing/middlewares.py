from django.conf import settings
from .models import PromotionToken


class PromotionTokenMiddleWare(object):
    def process_request(self, request):
        token = request.GET.get(settings.PROMO_TOKEN_QUERY_STRING, None)

        if token:
            request.session[settings.PROMO_TOKEN_QUERY_STRING] = token
            #record = PromotionToken.objects.filter(token=token).first()
            #if record:
            #    request.session[settings.PROMO_TOKEN_USER_SESSION_KEY] = record.pk
