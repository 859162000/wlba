# encoding: utf8
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, Context
from django.utils import timezone
from django.views.generic import TemplateView
from marketing.models import NewsAndReport, TimelySiteData
from marketing.utils import pc_data_generator
from misc.views import MiscRecommendProduction
from wanglibao_buy.models import FundHoldInfo
from wanglibao_p2p.models import P2PProduct, P2PRecord
from wanglibao_banner.models import Banner, Partner
from itertools import chain
from wanglibao_announcement.utility import AnnouncementHomepage, AnnouncementP2PNew
from wanglibao_p2p.models import P2PEquity
from django.core.urlresolvers import reverse
import re
import urlparse
from wanglibao_redis.backend import redis_backend
import json
import pickle
import datetime
import hashlib
from wanglibao import settings

class IndexView(TemplateView):
    template_name = 'index_new.jade'

    PRODUCT_LENGTH = 3

    def _period_3(self, p2p):
        return p2p.filter(Q(pay_method__contains=u'日计息') & Q(period__gte=30) & Q(period__lt=90) | ~Q(pay_method__contains=u'日计息') & Q(period__gte=1) & Q(period__lt=3))

    def _period_6(self, p2p):
        return p2p.filter(Q(pay_method__contains=u'日计息') & (Q(period__gte=90) & Q(period__lt=180)) | ~Q(pay_method__contains=u'日计息') & (Q(period__gte=3) & Q(period__lt=6)))

    def _period_9(self, p2p):
        return p2p.filter(Q(pay_method__contains=u'日计息') & Q(period__gte=180) | ~Q(pay_method__contains=u'日计息') & Q(period__gte=6))

    def _filter_product_period(self, p2p, period):
        if period == 3:
            p2p = self._period_3(p2p)
        elif period == 6:
            p2p = self._period_6(p2p)
        elif period == 9:
            p2p = self._period_9(p2p)

        return p2p

    def _full_product_payment(self, period, num, product_id=None):
        """ 查询满表且已经还款中的标 """
        p2p = P2PProduct.objects.select_related(
            'warrant_company', 'activity'
        ).filter(
            hide=False,
            publish_time__lte=timezone.now(),
            status=u'还款中'
        )
        if product_id:
            p2p = p2p.exclude(id=product_id)
        return self._filter_product_period(p2p, period).order_by('-soldout_time', '-priority')[:num]

    def _full_product_nonpayment(self, period, num, product_id=None):
        """ 查询满表但是非还款中的标 """
        p2p = P2PProduct.objects.select_related(
            'warrant_company', 'activity'
        ).filter(
            hide=False,
            publish_time__lte=timezone.now(),
            status__in=[u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核']
        )
        if product_id:
            p2p = p2p.exclude(id=product_id)
        return self._filter_product_period(p2p, period).order_by('-soldout_time', '-priority')[:num]

    def get_products(self, period, product_id=None):
        """ 查询符合条件的标列表
        3:1-3个月（包含3月）
        6:4-6个月（包含6个月）
        9:6个月以上
        """
        if period not in (3, 6, 9):
            return []
        p2p_list = []
        p2p = P2PProduct.objects.select_related(
            'warrant_company', 'activity'
        ).filter(
            hide=False, publish_time__lte=timezone.now(), status=u'正在招标'
        )

        if product_id:
            p2p = p2p.exclude(id=product_id)

        p2p = self._filter_product_period(p2p, period).order_by('-priority', '-total_amount')[:self.PRODUCT_LENGTH]
        p2p_list.extend(p2p)
        # 使用满标但是未还款的扩充
        if len(p2p_list) < self.PRODUCT_LENGTH:
            p2p_list.extend(self._full_product_nonpayment(period=period, num=self.PRODUCT_LENGTH-len(p2p_list), product_id=product_id))
        # 使用慢标且还款中的扩充
        if len(p2p_list) < self.PRODUCT_LENGTH:
            p2p_list.extend(self._full_product_payment(period=period, num=self.PRODUCT_LENGTH-len(p2p_list), product_id=product_id))
        return p2p_list

    def get_context_data(self, **kwargs):

        # 主推标
        recommend_product_id = None
        if self.request.user and self.request.user.is_authenticated():
            user = self.request.user
            product_new = P2PProduct.objects.filter(hide=False, status=u'正在招标', category=u'新手标')
            if product_new.exists():
                if not P2PRecord.objects.filter(user=user).exists():
                    # 不存在购买记录
                    id_rate = [{'id': q.id, 'rate': q.completion_rate} for q in product_new]
                    id_rate = sorted(id_rate, key=lambda x: x['rate'], reverse=True)
                    recommend_product_id = id_rate[0]['id']
                else:
                    # 存在购买记录
                    misc = MiscRecommendProduction()
                    recommend_product_id = misc.get_recommend_product_except_new()

        if not recommend_product_id:
            misc = MiscRecommendProduction()
            recommend_product_id = misc.get_recommend_product_id()

        recommend_product = P2PProduct.objects.filter(id=recommend_product_id)

        # p2p_products = []
        # 获取期限小于等于3个月的标，天数为90天(period<=3 or period<=90)
        p2p_lt3 = self.get_products(period=3, product_id=recommend_product_id)
        # 获取期限大雨3个月小于等于6个月的标，天数为180天(3<period<=6 or 90<period<=180)
        p2p_lt6 = self.get_products(period=6, product_id=recommend_product_id)
        # 获取期限大于6个月的标(period>6 or period>180)
        p2p_gt6 = self.get_products(period=9, product_id=recommend_product_id)
        getmore = True

        banners = Banner.objects.filter(Q(device=Banner.PC_2), Q(is_used=True), Q(is_long_used=True) | (Q(is_long_used=False) & Q(start_at__lte=timezone.now()) & Q(end_at__gte=timezone.now())))
        # 新闻页面只有4个固定位置
        news_and_reports = NewsAndReport.objects.all().order_by('-score', '-created_at')[:4]

        # 网站数据
        m = MiscRecommendProduction(key=MiscRecommendProduction.KEY_PC_DATA, desc=MiscRecommendProduction.DESC_PC_DATA)
        site_data = m.get_recommend_products()
        if site_data:
            site_data = site_data[MiscRecommendProduction.KEY_PC_DATA]
        else:
            site_data = pc_data_generator()
            m.update_value(value={MiscRecommendProduction.KEY_PC_DATA: site_data})
            # m.update_value(value=site_data)

        site_data['updated_at'] = m.get_misc().updated_at

        # 合作伙伴
        partners_data = Partner.objects.filter(type='partner')
        partners = [
            {'name': partner.name, 'link': partner.link, 'image': partner.image}
            for partner in partners_data
        ]

        # 公告 前7个
        annos = AnnouncementHomepage()[:7]

        # 总资产
        p2p_total_asset = 0
        fund_total_asset = 0
        if self.request.user and self.request.user.is_authenticated():
            user = self.request.user
            p2p_equities = P2PEquity.objects.filter(user=user, confirm=True).filter(product__status__in=[
                u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
            ]).select_related('product')

            unpayed_principle = 0
            for equity in p2p_equities:
                unpayed_principle += equity.unpaid_principal
            p2p_total_asset = user.margin.margin + user.margin.freeze + user.margin.withdrawing + unpayed_principle

            fund_hold_info = FundHoldInfo.objects.filter(user__exact=user)
            if fund_hold_info.exists():
                for hold_info in fund_hold_info:
                    fund_total_asset += hold_info.current_remain_share + hold_info.unpaid_income
            print partners
        return {
            "recommend_product": recommend_product,
            "p2p_lt_three": p2p_lt3,
            "p2p_lt_six": p2p_lt6,
            "p2p_gt_six": p2p_gt6,
            "news_and_reports": news_and_reports,
            'banners': banners,
            'site_data': site_data,
            'getmore': getmore,
            'announcements': annos,
            'announcements_p2p': AnnouncementP2PNew,
            'partners': partners,
            'p2p_total_asset': float(p2p_total_asset + fund_total_asset)
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
        # cache_backend = redis_backend()
        # partners = cache_backend.get_cache_partners()
        partners_data = Partner.objects.filter(type='partner')
        partners = [
            {'name': partner.name, 'link': partner.link, 'image': partner.image}
            for partner in partners_data
        ]

        return {
            'partners': partners
        }


class SecurityView(TemplateView):
    template_name = 'security_new.jade'

    def get_context_data(self, **kwargs):

        return {}


def page_not_found(request):
    template = loader.get_template('html/404.html')
    return HttpResponse(content=template.render(Context()), content_type='text/html; charset=utf-8', status=404)


def server_error(request):
    template = loader.get_template('html/500.html')
    return HttpResponse(content=template.render(Context()), content_type='text/html; charset=utf-8', status=500)

#
def landpage_view(request):
    """
    渠道跳转页，
    确定渠道来源，记录访问时间到redis中，
    跳转活动页
    :param request:
    :return:
    """
    channel_code = getattr(request, request.method).get('promo_token', None)
    activity_page = getattr(settings, '%s_ACTIVITY_PAGE' % channel_code.upper(), 'index')
    if channel_code and channel_code == getattr(settings, '%s_CHANNEL_CODE' % channel_code.upper(), None):
        # period 为结算周期，必须以天为单位
        period = getattr(settings, '%s_PERIOD' % channel_code.upper())
        # 设置tid默认值
        default_tid = getattr(settings, '%s_DEFAULT_TID' % channel_code.upper(), '')
        tid = getattr(request, request.method).get('tid', default_tid)
        if not tid and default_tid:
            tid = default_tid
        sign = getattr(request, request.method).get('sign', None)
        wlb_for_channel_key = getattr(settings, 'WLB_FOR_%s_KEY' % channel_code.upper())
        # 确定渠道来源
        if tid and sign == hashlib.md5(channel_code+str(wlb_for_channel_key)).hexdigest():
            redis = redis_backend()
            redis_channel_key = '%s_%s' % (channel_code, tid)
            land_time_lately = redis._get(redis_channel_key)
            current_time = datetime.datetime.now()
            # 如果上次访问的时间是在30天前则不更新访问时间
            if land_time_lately and tid != default_tid:
                land_time_lately = datetime.datetime.strptime(land_time_lately, '%Y-%m-%d %H:%M:%S')
                if land_time_lately + datetime.timedelta(seconds=180) <= current_time:
                    return HttpResponseRedirect(reverse(activity_page))
            redis._set(redis_channel_key, current_time.strftime("%Y-%m-%d %H:%M:%S"))
    return HttpResponseRedirect(reverse(activity_page))
