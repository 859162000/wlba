# encoding: utf8
from django.db.models import Q
from django.utils import timezone
from django.views.generic import TemplateView
from marketing.models import NewsAndReport
from wanglibao_p2p.models import P2PProduct, P2PRecord


class IndexView(TemplateView):
    template_name = 'index.jade'

    def get_context_data(self, **kwargs):
        p2p_products = P2PProduct.objects.filter(Q(publish_time__lte=timezone.now())).filter(Q(status=u'正在招标') | Q(status=u'已完成'))[:20]
        trade_records = P2PRecord.objects.filter(catalog=u'申购').prefetch_related('user').prefetch_related('user__wanglibaouserprofile')[:40]

        news_and_reports = NewsAndReport.objects.all()[:5]
        return {
            "p2p_products": p2p_products,
            "trade_records": trade_records,
            "news_and_reports": news_and_reports,
        }

