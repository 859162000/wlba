# encoding: utf8
from django.utils import timezone

from django.views.generic import TemplateView
from wanglibao_hotlist.models import HotTrust, HotFund, HotFinancing
from wanglibao_p2p.models import P2PProduct, P2PRecord


class IndexView(TemplateView):
    template_name = 'index.jade'

    def get_context_data(self, **kwargs):
        # p2p_products = P2PProduct.objects.filter(publish_time__lte=timezone.now())[:20]
        p2p_products = P2PProduct.objects.all()[:20]
        trade_records = P2PRecord.objects.all()[:40]
        return {
            "p2p_products": p2p_products,
            "trade_records": trade_records
        }

