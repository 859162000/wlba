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
from wanglibao_p2p.amortization_plan import get_amortization_plan
from decimal import *
from wanglibao_account.models import Binding


class IndexView(TemplateView):
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


class HomeView(TemplateView):
    template_name = 'mobile_index.jade'

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
        return {
            "p2p_products": p2p_products
        }
        
class DetailView(TemplateView):
    template_name = 'mobile_detail.jade'

    def get_context_data(self, id, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)

        try:
            #p2p = P2PProduct.objects.select_related('activity').get(pk=id, hide=False).exclude(status=u'流标')
            p2p = P2PProduct.objects.select_related('activity').exclude(status=u'流标').exclude(status=u'录标').get(pk=id, hide=False)

            if p2p.soldout_time:
                end_time = p2p.soldout_time
            else:
                end_time = p2p.end_time
        except P2PProduct.DoesNotExist:
            raise Http404(u'您查找的产品不存在')

        terms = get_amortization_plan(p2p.pay_method).generate(p2p.total_amount,
                                                               p2p.expected_earning_rate / 100,
                                                               p2p.amortization_count,
                                                               p2p.period)
        total_earning = terms.get("total") - p2p.total_amount
        total_fee_earning = 0

        if p2p.activity:
            total_fee_earning = Decimal(
                p2p.total_amount * p2p.activity.rule.rule_amount * (Decimal(p2p.period) / Decimal(12))).quantize(
                Decimal('0.01'))

        user = self.request.user
        current_equity = 0

        if user.is_authenticated():
            equity_record = p2p.equities.filter(user=user).first()
            if equity_record is not None:
                current_equity = equity_record.equity

            xunlei_vip = Binding.objects.filter(user=user).filter(btype='xunlei').first()
            context.update({
                'xunlei_vip': xunlei_vip
            })

        orderable_amount = min(p2p.limit_amount_per_user - current_equity, p2p.remain)

        site_data = SiteData.objects.all()[0]
        #排行榜


        context.update({
            'p2p': p2p,
            'end_time': end_time,
            'orderable_amount': orderable_amount,
            'total_earning': total_earning,
            'current_equity': current_equity,
            'site_data': site_data,
            'attachments': p2p.attachment_set.all(),
            'total_fee_earning': total_fee_earning
        })

        return context
