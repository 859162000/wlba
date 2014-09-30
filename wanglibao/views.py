# encoding: utf8
from django.db.models import Q
from django.http import HttpResponse
from django.template import loader, Context
from django.utils import timezone
from django.views.generic import TemplateView
from marketing.models import NewsAndReport, SiteData
from wanglibao_p2p.models import P2PProduct, P2PRecord
from wanglibao_banner.models import Banner
from itertools import chain


class IndexView(TemplateView):
    template_name = 'index.jade'

    def get_context_data(self, **kwargs):


        p2p_pre_three = P2PProduct.objects.filter(hide=False).filter(Q(publish_time__lte=timezone.now()))\
            .filter(status=u'正在招标').order_by('-priority', '-total_amount').select_related('warrant_company')[:4]

        p2p_middle = P2PProduct.objects.filter(hide=False).filter(Q(publish_time__lte=timezone.now()))\
            .filter(status__in=[
                u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核'
        ]).order_by('-priority', '-soldout_time').select_related('warrant_company')


        p2p_last = P2PProduct.objects.filter(hide=False).filter(Q(publish_time__lte=timezone.now()))\
            .filter(status=u'还款中').order_by('-priority', '-soldout_time').select_related('warrant_company')

        p2p_products = chain(p2p_pre_three[:3], p2p_middle, p2p_last)

        getmore = False
        if p2p_pre_three.count() > 3 and p2p_last:
            getmore = True

        trade_records = P2PRecord.objects.filter(catalog=u'申购').select_related('user').select_related('user__wanglibaouserprofile')[:11]
        banners = Banner.objects.filter(device=Banner.PC_2)
        news_and_reports = NewsAndReport.objects.all()[:5]
        site_data = SiteData.objects.all().first()

        return {
            "p2p_products": p2p_products,
            "trade_records": trade_records,
            "news_and_reports": news_and_reports,
            'banners': banners,
            'site_data': site_data,
            'getmore': getmore
        }


class SecurityView(TemplateView):
    template_name = 'security.jade'

    def get_context_data(self, **kwargs):

        return {}


def page_not_found(request):
    template = loader.get_template('html/404.html')
    return HttpResponse(content=template.render(Context()), content_type='text/html; charset=utf-8', status=404)


def server_error(request):
    template = loader.get_template('html/500.html')
    return HttpResponse(content=template.render(Context()), content_type='text/html; charset=utf-8', status=500)

