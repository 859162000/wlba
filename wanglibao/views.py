# encoding: utf8
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, Context
from django.utils import timezone
from django.views.generic import TemplateView
from marketing.models import NewsAndReport, SiteData
from wanglibao_p2p.models import P2PProduct, P2PRecord
from wanglibao_banner.models import Banner, Partner
from itertools import chain
from wanglibao_announcement.utility import AnnouncementHomepage, AnnouncementP2PNew
from django.core.urlresolvers import reverse
import re
import urlparse
from wanglibao_redis.backend import redis_backend
import json
import pickle


class IndexView(TemplateView):
    template_name = 'index.jade'

    def get_context_data(self, **kwargs):

        cache_backend = redis_backend()

        p2p_pre_four = P2PProduct.objects.select_related('warrant_company', 'activity')\
                                         .filter(hide=False).filter(Q(publish_time__lte=timezone.now()))\
                                         .filter(status=u'正在招标').order_by('-priority', '-total_amount')[:4]

        p2p_pre_four_list = cache_backend.get_p2p_list_from_objects(p2p_pre_four)

        p2p_products, p2p_full_list, p2p_repayment_list = [], [], []

        if cache_backend.redis.exists('p2p_products_full'):
            p2p_full_cache = cache_backend.redis.lrange('p2p_products_full', 0, -1)
            for product in p2p_full_cache:
                p2p_full_list.extend([pickle.loads(product)])
        else:
            p2p_full = P2PProduct.objects.select_related('warrant_company', 'activity') \
                .filter(hide=False).filter(Q(publish_time__lte=timezone.now())) \
                .filter(status__in=[u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核']) \
                .order_by('-soldout_time', '-priority')
            p2p_full_list = cache_backend.get_p2p_list_from_objects(p2p_full)

        if cache_backend.redis.exists('p2p_products_repayment'):
            p2p_repayment_cache = cache_backend.redis.lrange('p2p_products_repayment', 0, 1)

            for product in p2p_repayment_cache:
                p2p_repayment_list.extend([pickle.loads(product)])
        else:
            p2p_repayment = P2PProduct.objects.select_related('warrant_company', 'activity')\
                .filter(hide=False).filter(Q(publish_time__lte=timezone.now())) \
                .filter(status=u'还款中').order_by('-soldout_time', '-priority')[:2]

            p2p_repayment_list = cache_backend.get_p2p_list_from_objects(p2p_repayment)

        p2p_products.extend(p2p_pre_four_list)
        p2p_products.extend(p2p_full_list)
        p2p_products.extend(p2p_repayment_list)

        getmore = True

        trade_records = P2PRecord.objects.filter(catalog=u'申购').select_related('user').select_related('user__wanglibaouserprofile')[:20]
        # banners = Banner.objects.filter(device=Banner.PC_2)
        banners = Banner.objects.filter(Q(device=Banner.PC_2), Q(is_used=True), Q(is_long_used=True) | (Q(is_long_used=False) & Q(start_at__lte=timezone.now()) & Q(end_at__gte=timezone.now())))
        news_and_reports = NewsAndReport.objects.all().order_by("-score")[:5]
        site_data = SiteData.objects.all().first()

        partners = cache_backend.get_cache_partners()

        return {
            "p2p_products": p2p_products,
            "trade_records": trade_records,
            "news_and_reports": news_and_reports,
            'banners': banners,
            'site_data': site_data,
            'getmore': getmore,
            'announcements': AnnouncementHomepage,
            'announcements_p2p': AnnouncementP2PNew,
            'partners': partners,
        }

    def get(self, request, *args, **kwargs):
        device_list = ['android', 'iphone']
        referer = request.META.get("HTTP_REFERER", "")
        if referer:
            res = urlparse.urlparse(referer)
            if "baidu.com" in res.netloc:
                qs = urlparse.parse_qs(res.query)
                if "wd" in qs:
                    request.session["promo_source_word"] = "|".join(qs['wd'])
        user_agent = request.META.get('HTTP_USER_AGENT', "").lower()
        for device in device_list:
            match = re.search(device, user_agent)
            if match and match.group():
                return HttpResponseRedirect(reverse('weixin_p2p_list'))

        return super(IndexView, self).get(request, *args, **kwargs)


class PartnerView(TemplateView):
    template_name = 'partner.jade'

    def get_context_data(self, **kwargs):

        partners = cache_backend.get_cache_partners()

        return {
            'partners': partners
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

