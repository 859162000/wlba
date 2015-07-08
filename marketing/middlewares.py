# encoding:utf-8
from django.conf import settings
from .models import PromotionToken
from wanglibao_account.cooperation import CoopRegister


class PromotionTokenMiddleWare(object):
    def process_request(self, request):
        CoopRegister(request).all_processors_for_session()