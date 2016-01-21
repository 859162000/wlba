#!/usr/bin/env python
# encoding:utf-8

__author__ = 'zhanghe'

import logging
import json

from datetime import datetime, timedelta
from marketing.models import IntroducedBy
from marketing.tops import Top
from marketing.utils import local_to_utc
from misc.views import MiscRecommendProduction

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib import auth
from django.db.models import Q, Sum, Count
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.views.generic import TemplateView
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from wanglibao import settings
from wanglibao.templatetags.formatters import safe_phone_str
from wanglibao_account.models import UserPhoneBook
from wanglibao_account import backends as account_backends
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao_banner.models import AppActivate
from wanglibao_p2p.models import ProductAmortization, P2PEquity, P2PProduct, P2PRecord, \
    UserAmortization, AmortizationRecord
from wanglibao_p2p.serializers import P2PProductSerializer
from wanglibao_rest.utils import split_ua, get_client_ip
from wanglibao_banner.models import Banner
from wanglibao_sms import messages as sms_messages
from wanglibao_sms.utils import send_validation_code
from wanglibao_sms.tasks import send_messages
from wanglibao_anti.anti.anti import AntiForAllClient
from wanglibao_account.forms import verify_captcha
from wanglibao_app.questions import question_list
from wanglibao_margin.models import MarginRecord
from wanglibao_rest import utils
from wanglibao_activity.models import ActivityShow
from wanglibao_activity.utils import get_queryset_paginator, get_sorts_for_activity_show
from wanglibao_announcement.models import AppMemorabilia
from weixin.util import _generate_ajax_template
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger, EmptyPage
import re
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from wanglibao_rest.utils import split_ua

logger = logging.getLogger(__name__)

class AppActivateScoreImageAPIView(APIView):
    """
    app端查询启动评分活动图片
    """
    permission_classes = ()
    SIZE_MAP = {'1': 'img_one', '2': 'img_two', '3': 'img_three', '4': 'img_four'}
    DEVICE_MAP = {'ios': 'app_iso', 'android': 'app_android', 'act_iso': 'act_iso', 'act_android': 'act_android', 'act_score_iso': 'act_score_iso'}

    def post(self, request):
        size = request.DATA.get('size', '').strip()

        device = split_ua(request)
        device_type = device['device_type']

        if not device_type or not size:
            return Response({'ret_code': 20001, 'message': u'信息输入不完整'})

        if device_type != 'ios' or int(size) not in (x for x in range(1, 9)):
            return Response({'ret_code': 20002, 'message': u'参数不合法'})

        if int(size) in (x for x in range(5, 9)):
            size = str(int(size) - 4)
            device_type = 'act_score_iso'

        size = self.SIZE_MAP[size]

        activate = AppActivate.objects.filter(Q(is_used=True), Q(device=self.DEVICE_MAP[device_type]), Q(is_long_used=True) | (Q(is_long_used=False) & Q(start_at__lte=timezone.now()) & Q(end_at__gte=timezone.now()))).first()
        if activate:
            if size == 'img_one':
                img_url = activate.img_one
            elif size == 'img_two':
                img_url = activate.img_two
            elif size == 'img_three':
                img_url = activate.img_three
            elif size == 'img_four':
                img_url = activate.img_four
            else:
                img_url = ''

            if img_url:
                img_url = '{host}/media/{url}'.format(host=settings.CALLBACK_HOST, url=img_url)
                return Response({'ret_code': 0,
                                 'message': 'ok',
                                 'image': img_url,
                                 })

        return Response({'ret_code': 20003, 'message': 'fail'})



class AppActivateImageAPIView(APIView):
    """ app端查询启动活动图片 """
    permission_classes = (IsAuthenticated,)

    SIZE_MAP = {'1': 'img_one', '2': 'img_two', '3': 'img_three', '4': 'img_four'}
    DEVICE_MAP = {'ios': 'app_iso', 'android': 'app_android', 'act_iso': 'act_iso', 'act_android': 'act_android', 'act_score_iso': 'act_score_iso'}

    def post(self, request):
        size = request.DATA.get('size', '').strip()

        device = split_ua(request)
        device_type = device['device_type']

        if not device_type or not size:
            return Response({'ret_code': 20001, 'message': u'信息输入不完整'})

        if device_type not in ('ios', 'android') or int(size) not in (x for x in range(1, 9)):
            return Response({'ret_code': 20002, 'message': u'参数不合法'})

        if int(size) in (x for x in range(5, 9)):
            size = str(int(size) - 4)
            if device_type == 'ios': device_type = 'act_iso'
            if device_type == 'android': device_type = 'act_android'

        size = self.SIZE_MAP[size]

        activate = AppActivate.objects.filter(Q(is_used=True), Q(device=self.DEVICE_MAP[device_type]), Q(is_long_used=True) | (Q(is_long_used=False) & Q(start_at__lte=timezone.now()) & Q(end_at__gte=timezone.now()))).first()
        if activate:
            if size == 'img_one':
                img_url = activate.img_one
            elif size == 'img_two':
                img_url = activate.img_two
            elif size == 'img_three':
                img_url = activate.img_three
            elif size == 'img_four':
                img_url = activate.img_four
            else:
                img_url = ''
            jump_state = activate.jump_state
            link_dest = activate.link_dest
            if img_url:
                invest_flag = P2PRecord.objects.filter(user=request.user,catalog='申购').exists()
                if activate.user_invest_limit==-1 or (activate.user_invest_limit==0 and not invest_flag) or (activate.user_invest_limit==1 and invest_flag):
                    img_url = '{host}/media/{url}'.format(host=settings.CALLBACK_HOST, url=img_url)
                    return Response({'ret_code': 0,
                                     'message': 'ok',
                                     'image': img_url,
                                     'jump_state': jump_state,
                                     'link_dest':link_dest,
                                     'link_dest_url':activate.link_dest_h5_url,
                                     })

        return Response({'ret_code': 20003, 'message': 'fail'})


class AppRepaymentAPIView(APIView):
    """ app 首页当月还款和用户收益接口 """

    permission_classes = ()

    def post(self, request):
        now = datetime.now()
        amount, income_num, income_yesterday = 0, 0, 0
        try:
            if request.user and request.user.is_authenticated():
                # 登陆用户 查询当天收益和累计收益
                user = request.user
                start_utc = local_to_utc(now, 'min')
                yesterday_start = start_utc - timedelta(days=1)
                yesterday_end = yesterday_start + timedelta(hours=23, minutes=59, seconds=59)

                p2p_equities = P2PEquity.objects.filter(user=user, confirm=True, product__status__in=[
                    u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
                ]).select_related('product')
                for equity in p2p_equities:
                    amount += equity.pre_paid_interest  # 累积收益
                    amount += equity.pre_paid_coupon_interest  # 加息券加息收益
                    amount += equity.activity_interest  # 活动收益
                    # if equity.confirm_at >= start_utc:
                    #     income_num += equity.pre_paid_interest
                    #     income_num += equity.pre_paid_coupon_interest
                    #     income_num += equity.activity_interest

                # 昨日收益
                # 利息入账, 罚息入账, 活动赠送, 邀请赠送, 加息存入, 佣佣金存入, 全民淘金
                income_yesterday_other = MarginRecord.objects.filter(user=user)\
                    .filter(create_time__gt=yesterday_start, create_time__lte=yesterday_end)\
                    .filter(catalog__in=[u'利息入账', u'罚息入账', u'加息存入', u'佣金存入', u'全民淘金']).aggregate(Sum('amount'))

                if income_yesterday_other.get('amount__sum'):
                    income_yesterday += income_yesterday_other.get('amount__sum')

                return Response({
                    'ret_code': 0,
                    'message': 'ok',
                    'amount': float(amount),
                    'income_num': float(income_num),
                    'income_yesterday': float(income_yesterday)
                })

            else:
                # 未登陆用户 查询当月还款金额和当月还款项目
                start = datetime(now.year, now.month, 1)
                start_utc = local_to_utc(start, 'min')

                ams = ProductAmortization.objects.filter(settlement_time__range=(start_utc, timezone.now()), settled=True)
                for x in ams:
                    amount += x.principal + x.interest + x.penal_interest
                return Response({
                    'ret_code': 0,
                    'message': 'ok',
                    'amount': float(amount),
                    'income_num': len(ams),
                    'income_yesterday': float(income_yesterday)
                })
        except Exception, e:
            logger.error(e.message)
            return Response({'ret_code': 20001, 'message': 'fail'})


class AppRepaymentPlanAllAPIView(APIView):
    """ app 用户所有还款计划接口 """

    permission_classes = (IsAuthenticated, )

    def post(self, request):
        user = request.user
        page = request.DATA.get('page', 1)
        pagesize = request.DATA.get('num', 10)
        page = int(page)
        pagesize = int(pagesize)

        user_amortizations = UserAmortization.objects.filter(user=user)\
            .select_related('product_amortization').select_related('product_amortization__product')\
            .order_by('-term_date')
        if user_amortizations:
            paginator = Paginator(user_amortizations, pagesize)

            try:
                user_amortizations = paginator.page(page)
            except PageNotAnInteger:
                user_amortizations = paginator.page(1)
            except EmptyPage:
                user_amortizations = []
            except Exception:
                user_amortizations = paginator.page(paginator.num_pages)

            amo_list = _user_amortization_list(user_amortizations)
            count = paginator.num_pages
        else:
            amo_list = []
            count = 0
        return Response({'ret_code': 0, 'data': amo_list, 'page': page, 'num': pagesize, 'count': count})


class AppRepaymentPlanMonthAPIView(APIView):
    """ app 用户月份还款计划接口 """

    permission_classes = (IsAuthenticated, )

    def post(self, request):
        user = request.user
        now = datetime.now()
        request_year = request.DATA.get('year', '')
        request_month = request.DATA.get('month', '')
        year = request_year if request_year else now.year
        month = request_month if request_month else now.month
        # current_month = '{}-{}'.format(now.year, now.month)
        current_month = now.strftime('%Y-%m')


        start = local_to_utc(datetime(int(year), int(month), 1), 'min')
        if int(month) == 12:
            end = local_to_utc(datetime(int(year) + 1, 1, 1) - timedelta(days=1), 'max')
        else:
            end = local_to_utc(datetime(int(year), int(month) + 1, 1) - timedelta(days=1), 'max')

        # 月份/月还款金额/月还款期数
        if request_year and request_month:
            amos_group = UserAmortization.objects.filter(user=user)\
                .filter(term_date__gt=start, term_date__lte=end).order_by('term_date')\
                .extra({'term_date': "DATE_FORMAT(term_date,'%%Y-%%m')"}).values('term_date')\
                .annotate(Count('term_date')).annotate(Sum('principal')).annotate(Sum('interest'))\
                .annotate(Sum('penal_interest')).annotate(Sum('coupon_interest')).order_by('term_date')
        else:
            amos_group = UserAmortization.objects.filter(user=user)\
                .extra({'term_date': "DATE_FORMAT(term_date,'%%Y-%%m')"}).values('term_date')\
                .annotate(Count('term_date')).annotate(Sum('principal')).annotate(Sum('interest'))\
                .annotate(Sum('penal_interest')).annotate(Sum('coupon_interest')).order_by('term_date')

        month_group = [{
            'term_date': amo.get('term_date'),
            'term_date_count': amo.get('term_date__count'),
            'total_sum': amo.get('principal__sum') + amo.get('interest__sum') +
                         amo.get('penal_interest__sum') + amo.get('coupon_interest__sum'),
            'principal_sum': amo.get('principal__sum'),
            'interest_sum': amo.get('interest__sum'),
            'penal_interest_sum': amo.get('penal_interest__sum'),
            'coupon_interest_sum': amo.get('coupon_interest__sum'),
        } for amo in amos_group]

        # 当月的还款计划
        user_amortizations = UserAmortization.objects.filter(user=user)\
            .filter(term_date__gt=start, term_date__lte=end)\
            .select_related('product_amortization').select_related('product_amortization__product')\
            .order_by('term_date')
        if user_amortizations:
            amo_list = _user_amortization_list(user_amortizations)
        else:
            amo_list = []

        if not amo_list:
            custom_month_data = {
                'term_date': current_month,
                'term_date_count': 0,
                'total_sum': 0.0,
                'principal_sum': 0.0,
                'interest_sum': 0.0,
                'penal_interest_sum': 0.0,
                'coupon_interest_sum': 0.0,
            }
            month_group.append(custom_month_data)
            month_group.sort(key=lambda x: x['term_date'])

        return Response({'ret_code': 0,
                         'data': amo_list,
                         'month_group': month_group,
                         'current_month': current_month,
                         })


def _user_amortization_list(user_amortizations):
    amo_list = []
    for amo in user_amortizations:
        if amo.settled:
            if amo.settlement_time.strftime('%Y-%m-%d') < amo.term_date.strftime('%Y-%m-%d'):
                status = u'提前回款'
            else:
                status = u'已回款'
        else:
            status = u'待回款'
        amo_list.append({
            'user_amortization_id': amo.id,
            'product_amortization_id': amo.product_amortization.id,
            'product_id': amo.product_amortization.product.id,
            'product_name': amo.product_amortization.product.name,
            'term': amo.term,
            'term_total': amo.product_amortization.product.amortization_count,
            'term_date': amo.term_date,
            'principal': amo.principal,
            'interest': amo.interest,
            'penal_interest': amo.penal_interest,
            'coupon_interest': amo.coupon_interest,
            'total_interest': amo.interest + amo.penal_interest + amo.coupon_interest,  # 总利息
            'settled': amo.settled,
            'settlement_time': amo.settlement_time,
            'settlement_status': status
        })
    return amo_list


class AppDayListView(TemplateView):
    """ app端榜单 """
    template_name = 'client_daylist.jade'

    def get_context_data(self, **kwargs):

        top = Top(limit=10)
        top_list = top.day_tops_activate(day=datetime.now(), amount_min=0)
        return {
            'top_list': top_list,
        }


class AppGuardView(TemplateView):
    """ app保障页面 """
    template_name = 'client_secure.jade'

class AppGuideView(TemplateView):
    """ app新手引导页面 """
    template_name = 'client_guide.jade'

class AppSecureView(TemplateView):
    """ app安全保障页面"""
    template_name = ''

class AppExploreView(TemplateView):
    """ app发现页面 """

    # template_name = 'client_discover.jade'
    #
    # def get_context_data(self, **kwargs):
    #     #banner = Banner.objects.filter(device='mobile', type='banner', is_used=True).order_by('-priority')
    #     banner = Banner.objects.filter(Q(device='mobile'), Q(is_used=True), Q(is_long_used=True) | (Q(is_long_used=False) & Q(start_at__lte=timezone.now()) & Q(end_at__gte=timezone.now()))).order_by('-priority')
    #     return {
    #         'banner': banner,
    #     }


    template_name = 'client_area.jade'

    def get_context_data(self, **kwargs):
        activity_list = ActivityShow.objects.filter(link_is_hide=False,
                                                    is_app=True,
                                                    start_at__lte=timezone.now(),
                                                    end_at__gt=timezone.now()
                                                    ).select_related('activity')

        limit = 6
        page = 1

        activity_list = get_sorts_for_activity_show(activity_list)

        activity_list, all_page, data_count = get_queryset_paginator(activity_list, 1, limit)

        return {
            'results': activity_list[:limit],
            'all_page': all_page,
            'page': page
        }

class AppManagementView(TemplateView):
    """ app管理团队 """
    template_name = 'client_management.jade'

class AppAboutView(TemplateView):
    """ app关于网利宝 """
    template_name = 'client_about.jade'

class AppP2PProductViewSet(PaginatedModelViewSet):
    """ app查询标列表接口 """

    model = P2PProduct
    permission_classes = (IsAdminUserOrReadOnly,)
    serializer_class = P2PProductSerializer
    paginate_by = 20

    def get_queryset(self):
        qs = super(AppP2PProductViewSet, self).get_queryset()

        maxid = self.request.QUERY_PARAMS.get('maxid', '')
        minid = self.request.QUERY_PARAMS.get('minid', '')

        pager = None
        if maxid and not minid:
            pager = Q(id__gt=maxid)
        if minid and not maxid:
            pager = Q(id__lt=minid)

        manual = u"FIELD({column}, '正在招标', '满标待审核', '满标已审核', '满标待打款', '满标已打款','还款中')".format(column='status')

        if pager:
            return qs.filter(hide=False, publish_time__lte=timezone.now()).filter(status__in=[
                u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标'
            ]).exclude(Q(category=u'票据') | Q(category=u'酒仙众筹标')).filter(pager)\
                .extra(select={'manual': manual}, order_by=['manual', '-priority', '-publish_time'])
        else:
            return qs.filter(hide=False, publish_time__lte=timezone.now()).filter(status__in=[
                u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标'
            ]).exclude(Q(category=u'票据') | Q(category=u'酒仙众筹标'))\
                .extra(select={'manual': manual}, order_by=['manual', '-priority', '-publish_time'])


class AppRecommendViewSet(PaginatedModelViewSet):
    """ app查询主推标接口
    如果设置了主推标，按照设置的顺序显示
    如果没有设置主推标，那就查找最近一个将要买完的显示
    """
    model = P2PProduct
    permission_classes = (IsAdminUserOrReadOnly,)
    serializer_class = P2PProductSerializer
    paginate_by = 1

    def get_queryset(self):
        qs = super(AppRecommendViewSet, self).get_queryset()

        # 主推标
        recommend_product_id = None
        if self.request.user and self.request.user.is_authenticated():
            user = self.request.user
            product_new = P2PProduct.objects.filter(hide=False, publish_time__lte=timezone.now(),
                                                    status=u'正在招标', category=u'新手标')
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

        return qs.filter(id=recommend_product_id)


class RecommendProductManagerView(TemplateView):
    """ 推荐标的管理 """
    template_name = 'client_recommend_production.jade'

    def _get_product(self, id):
        if isinstance(id, list):
            return P2PProduct.objects.filter(id__in=id, publish_time__lte=timezone.now()).order_by('-id')
        else:
            return P2PProduct.objects.filter(id=id, publish_time__lte=timezone.now()).order_by('-id')

    def get_context_data(self, **kwargs):
        p2p_list = []
        misc = MiscRecommendProduction()
        ids = misc.get_recommend_products()
        if ids:
            products = P2PProduct.objects.filter(id__in=ids, publish_time__lte=timezone.now())
            for product in products:
                p2p_list.append({
                    'id': product.id,
                    'name': product.name,
                    'total_amount': product.total_amount,
                })

            p2p_list = sorted(p2p_list, key=lambda x: ids.index(x['id']))

        return {'p2p_list': p2p_list}

    def post(self, request, **kwargs):
        """ 添加删除 """
        operate = request.POST.get('manager')
        product_id = request.POST.get('product_id')
        if not operate or not product_id:
            messages.warning(request, u'请填写标的id')
            return redirect('./recommend_manager')

        if product_id and not product_id.isdigit():
            messages.warning(request, u'标的id不合法')
            return redirect('./recommend_manager')

        try:
            product_id = int(product_id)
            misc = MiscRecommendProduction()
            ids = misc.get_recommend_products()

            product = self._get_product(product_id)
            if not product:
                messages.warning(request, u'不存在id对应的标')
                return redirect('./recommend_manager')

            if operate == 'add':
                if product_id in ids:
                    messages.warning(request, u'此标已经被设置，不允许重复设置')
                    return redirect('./recommend_manager')

                if misc.add_product(product_id=product_id):
                    messages.warning(request, u'增加成功')
                    return redirect('./recommend_manager')

                messages.warning(request, u'增加失败')
                return redirect('./recommend_manager')

            elif operate == 'del':
                if product_id not in ids:
                    messages.warning(request, u'此标未被设置')
                    return redirect('./recommend_manager')

                if misc.del_product(product_id=product_id):
                    messages.warning(request, u'删除成功')
                    return redirect('./recommend_manager')

                messages.warning(request, u'删除失败')
                return redirect('./recommend_manager')

            return redirect('./recommend_manager')
        except Exception, e:
            logging.error(e.message)
            return redirect('./recommend_manager')


class SendValidationCodeView(APIView):
    """ app端获取验证码，不在设置状态码， """
    permission_classes = ()

    def post(self, request, phone):
        """
            modified by: Yihen@20150813
            descrpition: if(line299~line304)的修改，app端增加图片校验码验证
        """
        phone_number = phone.strip()
        if not AntiForAllClient(request).anti_special_channel():
            res, message = False, u"请输入验证码"
        else:
            res, message = verify_captcha(request.POST)
        if not res:
            return Response({"ret_code": 40044, "message": message})

        # ext=777,为短信通道内部的发送渠道区分标识
        # 仅在用户注册时使用
        status, message = send_validation_code(phone_number, ip=get_client_ip(request), ext='777')
        if status != 200:
            return Response({"ret_code": 30044, "message": message})

        return Response({"ret_code": 0, "message": u'验证码发送成功'})


class SendValidationCodeNoCaptchaView(APIView):
    """ app端获取验证码，不在设置状态码， """
    permission_classes = ()

    def post(self, request, phone):
        phone_number = phone.strip()

        status, message = send_validation_code(phone_number, ip=get_client_ip(request))
        if status != 200:
            return Response({"ret_code": 30044, "message": message})

        return Response({"ret_code": 0, "message": u'验证码发送成功'})


class AppIncomeMiscTemplateView(TemplateView):
    """ 设置收益比例参数"""
    template_name = "client_income_misc.jade"

    def get_context_data(self, **kwargs):
        data = {'rate_wlb': 100, 'rate_p2p': 80, 'rate_fund': 60, 'rate_bank': 40}
        m = MiscRecommendProduction(key=MiscRecommendProduction.KEY_INCOME_DATA, desc=MiscRecommendProduction.DESC_INCOME_DATA, data=data)
        return {'income': m.get_recommend_products()}

    def post(self, request, **kwargs):
        rate_wlb = request.POST.get('rate_wlb', '')
        rate_p2p = request.POST.get('rate_p2p', '')
        rate_fund = request.POST.get('rate_fund', '')
        rate_bank = request.POST.get('rate_bank', '')
        if not rate_wlb or not rate_p2p or not rate_fund or not rate_bank:
            messages.warning(request, u'输入数据不合法')
            return redirect('./income_misc')

        data = {'rate_wlb': rate_wlb, 'rate_p2p': rate_p2p, 'rate_fund': rate_fund, 'rate_bank': rate_bank}
        try:
            m = MiscRecommendProduction(key=MiscRecommendProduction.KEY_INCOME_DATA)
            m.update_value(value=data)
            messages.warning(request, u'数据新增(修改)成功')
            return redirect('./income_misc')
        except:
            messages.warning(request, u'系统错误，请联系开发人员')
            return redirect('./income_misc')


class AppIncomeRateAPIView(APIView):
    """ 查询获取收益比例配置信息 """
    permission_classes = ()

    def post(self, request):
        try:
            m = MiscRecommendProduction(key=MiscRecommendProduction.KEY_INCOME_DATA)
            rate = m.get_recommend_products()
            if rate:
                return Response({'ret_code': 0, 'message': '成功', 'rate': rate})
            else:
                return Response({'ret_code': 20001, 'message': u'请联系管理员配置收益比例数据'})
        except Exception, e:
            logger.error(e.message)
            return Response({'ret_code': 20002, 'message': 'fail'})


class AppPhoneBookUploadAPIView(APIView):
    """ user uploading phone book """
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        user = request.user

        phones = request.DATA.get('phones', '')
        if not phones:
            return Response({'ret_code': 20001, 'message': u'数据输入不合法'})
        phones = json.loads(phones)
        try:
            UserPhoneBook.objects.filter(user=user).exclude(phone__in=phones.keys()).update(is_used=False)
            phone_db = [u.get('phone') for u in UserPhoneBook.objects.filter(user=user, phone__in=phones.keys()).values('phone')]

            phone_new_list = []
            for p in phones.keys():
                if p in phone_db:
                    UserPhoneBook.objects.filter(user=user, phone=p).update(name=phones.get(p), is_used=True)
                else:
                    phone_book = UserPhoneBook()
                    phone_book.user = user
                    phone_book.phone = p
                    phone_book.name = phones.get(p)
                    if User.objects.filter(wanglibaouserprofile__phone=p).exists():
                        phone_book.is_register = True
                    else:
                        phone_book.is_register = False

                    if IntroducedBy.objects.filter(introduced_by=user, user__wanglibaouserprofile__phone=p).exists():
                        phone_book.is_invite = True
                    else:
                        phone_book.is_invite = False

                    phone_book.is_used = True
                    phone_new_list.append(phone_book)
            if phone_new_list:
                UserPhoneBook.objects.bulk_create(phone_new_list)
            return Response({'ret_code': 0, 'message': 'success'})
        except Exception, e:
            logger.error(e.message)
            return Response({'ret_code': 20002, 'message': u'同步通讯录错误'})


class AppPhoneBookQueryAPIView(APIView):
    """ 查询未邀请好友，即用户未注册 """
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        phone_book = UserPhoneBook.objects.filter(user=request.user, is_used=True, is_register=False)

        books, register_list = list(), list()
        for book in phone_book:
            if User.objects.filter(wanglibaouserprofile__phone=book.phone).exists():
                register_list.append(book.phone)
            else:
                books.append({
                    'name': book.name,
                    'phone': book.phone,
                    'status': True if not(book.invite_at and book.invite_at > local_to_utc(datetime.now(), 'min')) else False,
                    }
                )

        if register_list:
            UserPhoneBook.objects.filter(user=request.user, phone__in=register_list).update(is_register=True)

        return Response({'ret_code': 0, 'message': 'success', 'books': books})


class AppPhoneBookAlertApiView(APIView):
    """ 邀请注册和提醒投资接口
    flag:   1 invite user to register
            2 alert user to invest
    """
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        user = request.user
        flag = request.DATA.get('flag')
        phone = request.DATA.get('phone')
        if not phone or not flag or (flag and int(flag) not in(1, 2)):
            return Response({'ret_code': 20001, 'message': u'数据输入不合法'})

        try:
            user_book = UserPhoneBook.objects.filter(user=user, phone=phone).first()
            if not user_book:
                return Response({'ret_code': 20002, 'message': u'被提醒用户不存在'})

            profile = user.wanglibaouserprofile
            send_name = profile.name if profile.id_is_valid else safe_phone_str(profile.phone)
            # 投资提醒
            if int(flag) == 1:
                if not (user_book.alert_at and user_book.alert_at > local_to_utc(datetime.now(), 'min')):
                    self._send_sms(phone, sms_messages.sms_alert_invest(name=send_name))
                    user_book.alert_at = timezone.now()
                    user_book.is_used = True
                    user_book.save()
            # 邀请提醒
            elif int(flag) == 2:
                if User.objects.filter(wanglibaouserprofile__phone=phone).exists():
                    user_book.is_register = True
                    if IntroducedBy.objects.filter(introduced_by=user, user_wanglibaouserprofile__phone=phone).exists():
                        user_book.is_invite = True
                        user_book.is_used = True
                    user_book.save()

                if not user_book.is_register and not (user_book.invite_at and user_book.invite_at > local_to_utc(datetime.now(), 'min')):
                    self._send_sms(phone, sms_messages.sms_alert_invite(name=send_name, phone=profile.phone))
                    user_book.invite_at = timezone.now()
                    user_book.save()

            return Response({'ret_code': 0, 'message': 'ok'})
        except Exception, e:
            logger.error(e.message)
            return Response({'ret_code': 20003, 'message': u'内部程序错误'})

    def _send_sms(self, phone, sms):
        send_messages.apply_async(kwargs={
            'phones': [phone],
            'messages': [sms],
            'ext': 666  # 营销类短信发送必须增加ext参数,值为666
        })


class AppInviteAllGoldAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    def post(self, request, **kwargs):
        dic = account_backends.broker_invite_list(request.user)
        users = dic['users']
        first_amount, first_earning, second_amount, second_earning = dic['first_amount'],\
                dic['first_earning'], dic['second_amount'], dic['second_earning']
        first_count, second_count = dic['first_count'], dic['second_count']
        first_intro = dic['first_intro']
        commission = dic['commission']

        introduces = IntroducedBy.objects.filter(introduced_by=request.user).select_related("user__wanglibaouserprofile").all()
        keys = commission.keys()
        for x in introduces:
            user_id = x.user.id
            alert_invest = self._alert_invest_status(user=request.user, phone_user=x.user)
            if user_id in keys:
                first_intro.append([users[user_id].phone, commission[user_id]['amount'], commission[user_id]['earning'], alert_invest, x.created_at])
            else:
                first_intro.append([x.user.wanglibaouserprofile.phone, 0, 0, alert_invest, x.created_at])

        first_intro = sorted(first_intro, key=lambda l: (l[1], l[4]), reverse=True)

        return Response({"ret_code":0, "first":{"amount":first_amount,
                        "earning":first_earning, "count":first_count, "intro":first_intro},
                        "second":{"amount":second_amount, "earning":second_earning,
                        "count":second_count}, "count":len(introduces)})

    def _alert_invest_status(self, user, phone_user):
        try:
            profile = phone_user.wanglibaouserprofile
            phone_book = UserPhoneBook.objects.filter(user=user, phone=profile.phone).first()
            if phone_book:
                if not(phone_book.alert_at and phone_book.alert_at > local_to_utc(datetime.now(), 'min')):
                    phone_book.is_used = True
                    phone_book.save()
                    return True
            else:
                phone_book = UserPhoneBook()
                phone_book.user = user
                phone_book.phone = profile.phone
                phone_book.name = profile.name
                phone_book.is_register = True
                phone_book.is_invite = True
                phone_book.is_used = True
                phone_book.save()
                return True
            return False
        except Exception, e:
            return False


class AppLogoutAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, **kwargs):
        auth.logout(request)
        return Response({'ret_code': 0, 'message': 'success'})


class AppQuestionsView(TemplateView):

    """ app常见问题 """
    template_name = 'client_questions.jade'

    def get_context_data(self, **kwargs):

        list = []

        for val in sorted(question_list):
            list.append({
                'id': val,
                'question': question_list[val]['question']
            })

        return {
            "list": list,
        }


class AppQuestionsResultView(TemplateView):

    """ app常见问题 """
    template_name = 'client_questions_result.jade'

    def get_context_data(self, **kwargs):

        index = kwargs['index']

        que_list = question_list[index]

        result_title = que_list['question']
        result_list = que_list['answer']
        print result_title
        return {
            'title': result_title,
            "list": result_list,
        }


class AppCostView(TemplateView):

    """ 费用说明 """
    template_name = 'client_cost_description.jade'


class AppAreaView(TemplateView):
    """ 最新活动 """
    template_name = 'client_area.jade'

    def get_context_data(self, **kwargs):
        activity_list = ActivityShow.objects.filter(link_is_hide=False,
                                                    is_app=True,
                                                    start_at__lte=timezone.now(),
                                                    end_at__gt=timezone.now()
                                                    ).select_related('activity')

        limit = 6
        page = 1

        activity_list = get_sorts_for_activity_show(activity_list)

        activity_list, all_page, data_count = get_queryset_paginator(activity_list, 1, limit)

        return {
            'results': activity_list[:limit],
            'all_page': all_page,
            'page': page
        }

class AppAreaApiView(APIView):
    permission_classes = ()

    @property
    def allowed_methods(self):
        return ['GET']

    def get(self, request):

        template_name = 'include/ajax/ajax_area_latest.jade'

        activity_list = ActivityShow.objects.filter(link_is_hide=False,
                                                    is_app=True,
                                                    start_at__lte=timezone.now(),
                                                    end_at__gt=timezone.now(),
                                                    ).select_related('activity')

        activity_list = get_sorts_for_activity_show(activity_list)

        page = request.GET.get('page', 1)
        pagesize = request.GET.get('pagesize', 6)
        page = int(page)
        pagesize = int(pagesize)

        activity_list, all_page, data_count = get_queryset_paginator(activity_list,
                                                                     page, pagesize)

        html_data = _generate_ajax_template(activity_list, template_name)

        return Response({
            'html_data': html_data,
            'page': page,
            'all_page': all_page,
        })


class AppMemorabiliaView(APIView):
    permission_classes = ()

    @property
    def allowed_methods(self):
        return ['GET']

    def get(self, request):
        template_name = 'include/ajax/ajax_area_milepost.jade'

        memorabilias = AppMemorabilia.objects.filter(hide_link=False,
                                                     start_time__lte=timezone.now()
                                                     ).order_by('-priority')

        page = request.GET.get('page', 1)
        pagesize = request.GET.get('pagesize', 5)
        page = int(page)
        pagesize = int(pagesize)

        memorabilias, all_page, data_count = get_queryset_paginator(memorabilias,
                                                                    page, pagesize)

        html_data = _generate_ajax_template(memorabilias, template_name)

        return Response({
            'html_data': html_data,
            'page': page,
            'all_page': all_page,
            'list_count': data_count
        })

class AppDataModuleView(TemplateView):

    """ 数据魔方 """
    template_name = 'client_data_cube.jade'

class AppFinanceView(TemplateView):

    """ 投资记 """
    template_name = 'client_animate_finance.jade'

    def get(self, request, *args, **kwargs):

        device_list = ['wlbapp']
        user_agent = request.META.get('HTTP_USER_AGENT', "").lower()

        for device in device_list:
            match = re.search(device, user_agent)
            if match and match.group():
                return super(AppFinanceView, self).get(request, *args, **kwargs)
        return super(AppFinanceView, self).get(request, *args, **kwargs)
        #return HttpResponseRedirect(reverse('app_finance'))



# class AppMemorabiliaDetailView(TemplateView):
#     template_name = 'memorabilia_detail.jade'
#
#     def get_context_data(self, id, **kwargs):
#         context = super(AppMemorabiliaDetailView, self).get_context_data(**kwargs)
#
#         try:
#             memorabilia = (AppMemorabilia.objects.get(pk=id,
#                                                       hide_link=False,
#                                                       start_time__lte=timezone.now()))
#
#         except AppMemorabilia.DoesNotExist:
#             raise Http404(u'您查找的大事记不存在')
#
#         context.update({
#             'memorabilia': memorabilia,
#
#         })
#
#         return context


# class AppMemorabiliaPreviewView(TemplateView):
#     template_name = 'app_memorabilia_preview.jade'
#
#     def get_context_data(self, id, **kwargs):
#         context = super(AppMemorabiliaPreviewView, self).get_context_data(**kwargs)
#
#         try:
#             memorabilia = AppMemorabilia.objects.get(pk=id)
#
#         except AppMemorabilia.DoesNotExist:
#             raise Http404(u'您查找的大事记不存在')
#
#         context.update({
#             'memorabilia': memorabilia,
#
#         })
#
#         return context
