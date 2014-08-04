# encoding: utf8
from django.db.models import Q
from django.utils import timezone
from django.views.generic import TemplateView
from marketing.models import NewsAndReport, SiteData
from wanglibao_p2p.models import P2PProduct, P2PRecord
from wanglibao_banner.models import Banner
from statsd import statsd


class IndexView(TemplateView):
    template_name = 'index.jade'

    def get_context_data(self, **kwargs):
        p2p_products = P2PProduct.objects.filter(Q(publish_time__lte=timezone.now())).filter(
            status__in=[u'正在招标', u'已完成', u'满标待打款', u'满标待审核', u'还款中']).order_by('-end_time')[:20]
        trade_records = P2PRecord.objects.filter(catalog=u'申购').prefetch_related('user').prefetch_related('user__wanglibaouserprofile')[:40]
        banners = Banner.objects.filter(device=Banner.PC)
        news_and_reports = NewsAndReport.objects.all()[:5]
        site_data = SiteData.objects.all().first()

        return {
            "p2p_products": p2p_products,
            "trade_records": trade_records,
            "news_and_reports": news_and_reports,
            'banners': banners,
            'site_data': site_data
        }

class SecurityView(TemplateView):
    template_name = 'security.jade'

    def get_context_data(self, **kwargs):

        return {}
