#!/usr/bin/env python
# encoding:utf-8

from django.db.models import Q
from django.http import HttpResponse
from django.template import loader, Context
from django.utils import timezone
from django.views.generic import TemplateView
from datetime import datetime
from marketing.models import NewsAndReport, SiteData
from marketing.tops import Top
from wanglibao_p2p.models import P2PProduct, P2PRecord
from wanglibao_banner.models import Banner, Partner
from itertools import chain
from wanglibao_announcement.utility import AnnouncementHomepage, AnnouncementP2PNew


class HomeView(TemplateView):
    template_name = 'mobile_home.jade'


    def get_context_data(self, **kwargs):
        p2p_pre_four = P2PProduct.objects.select_related('warrant_company', 'activity').filter(hide=False).filter(Q(publish_time__lte=timezone.now()))\
            .filter(status=u'正在招标').order_by('-priority', '-total_amount')[:4]

        p2p_middle = P2PProduct.objects.select_related('warrant_company','activity').filter(hide=False).filter(Q(publish_time__lte=timezone.now()))\
            .filter(status__in=[
                u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核'
        ]).order_by('-soldout_time', '-priority')


        p2p_last = P2PProduct.objects.select_related('warrant_company', 'activity').filter(hide=False).filter(Q(publish_time__lte=timezone.now()))\
            .filter(status=u'还款中').order_by('-soldout_time', '-priority')[:2]

        p2p_products = chain(p2p_pre_four, p2p_middle, p2p_last)

        getmore = False
        if p2p_pre_four.count() > 3 and p2p_last:
            getmore = True

        trade_records = P2PRecord.objects.filter(catalog=u'申购').select_related('user').select_related('user__wanglibaouserprofile')[:20]
        banners = Banner.objects.filter(device=Banner.PC_2)
        news_and_reports = NewsAndReport.objects.all().order_by("-score")[:5]
        site_data = SiteData.objects.all().first()
        partners = Partner.objects.filter(type='partner')

        #排行榜

        top = Top()
        day_tops = top.day_tops(datetime.now())
        week_tops = top.week_tops(datetime.now())
        all_tops = top.all_tops()

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
            'day_tops': day_tops,
            'week_tops': week_tops,
            'all_tops': all_tops,
            'is_valid': top.is_valid()
        }


class TestView(TemplateView):
    template_name = 'test.jade'

    def get_context_data(self, **kwargs):
        return {}
