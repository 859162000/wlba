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

from django.contrib.auth.models import User
from django.views.generic import RedirectView
from wanglibao_account.utils import detect_identifier_type


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


class AccountRedirectView(RedirectView):
    """
    移动端用户首先输入手机号，点击下一步。
    以get方式请求此视图，并把用户输入得手机号通过参数传入
    判断手机号是否注册
    注册过的跳转登录页面
    未注册的跳转注册页面
    跳转过程中会将用户手机号以参数的形式传入
    """
    # 移动端登录页面
    mobile_login_url = '/mobile/account/login/'
    # 移动端注册页面
    mobile_register_url = '/mobile/account/register/'

    def get_redirect_url(self, *args, **kwargs):
        # 判断是否为手机号
        identifier_type = detect_identifier_type(kwargs.get('identifier'))
        if identifier_type != 'phone':
            # 不是手机号，跳转原地址并附带参数
            return '%s?identifier=%s&is_phone=false' % (kwargs.get('referer_url').split('?')[0], kwargs.get('identifier'))

        # 判断手机号是否已注册
        is_registered = User.objects.filter(wanglibaouserprofile__phone=kwargs.get('identifier')).count()
        is_registered = bool(is_registered)
        # 如果手机号已注册，跳转到登录页面
        # 如果手机号未注册，跳转到注册页面
        redirect_url = [self.mobile_register_url, self.mobile_login_url][is_registered]
        return '%s?identifier=%s' % (redirect_url, kwargs.get('identifier'))

    def get(self, request, *args, **kwargs):
        # 通过get方式传入用户手机号
        kwargs['identifier'] = request.GET.get('identifier')
        kwargs['referer_url'] = request.META.get('HTTP_REFERER')
        return super(AccountRedirectView, self).get(request, *args, **kwargs)


from collections import OrderedDict
import uuid
import time
import hashlib
import json
from .weixin import get_access_token, get_jsapi_ticket
APP_ID = 'wx4bf8abb47962a812'
APP_SECRET = '45066980fd1fa0c6bd06653f08da46aa'


def weixin_config(request):
    url = request.META.get('HTTP_REFERER', '') or request.GET.get('url', '')

    if not url:
        return HttpResponse(json.dumps({
            'errcode': 1,
            'msg': u'不能获取url'
        }), content_type="application/json")

    try:
        access_token = get_access_token(APP_ID, APP_SECRET).get('access_token')
        jsapi_ticket = get_jsapi_ticket(access_token).get('ticket')
        assert jsapi_ticket
    except Exception, e:
        return HttpResponse(json.dumps({
            'errcode': 1,
            'errmsg': e.message,
            'msg': u'请求微信接口错误'
        }), content_type="application/json")

    params = OrderedDict()
    params['jsapi_ticket'] = jsapi_ticket
    params['noncestr'] = uuid.uuid1().hex
    params['timestamp'] = str(int(time.time()))
    params['url'] = url.split('#')[0]
    string = '&'.join(['%s=%s' % (k, v) for k, v in params.items()])

    data = {
        'noncestr': params.get('noncestr'),
        'timestamp': params.get('timestamp'),
        'signature': hashlib.sha1(string).hexdigest()
    }

    return HttpResponse(json.dumps(data), content_type="application/json")