# coding=utf-8

import logging
from decimal import Decimal
from django.utils import timezone
from django.views.generic import TemplateView
from django.http import HttpResponseForbidden, Http404
from django.db.models import Sum
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from wanglibao_p2p.models import P2PProduct, UserAmortization, P2PRecord
from wanglibao.const import ErrorNumber
from wanglibao_sms.tasks import send_messages
from marketing.models import (RevenueExchangeAmortization as ExchangeAmo, RevenueExchangeRule,
                              RevenueExchangeRepertory)
from marketing.utils import generate_revenue_exchange_order
from .forms import FuelCardBuyForm
from .trade import P2PTrader
from .utils import get_sorts_for_created_time, get_p2p_reward_using_range

logger = logging.getLogger(__name__)


def get_user_revenue_count_for_type(user, product_type):
    """根据产品类型获取用户自注册起至今总收益"""

    revenue_count = Decimal('0.00')
    exchange_amos = ExchangeAmo.objects.filter(user=user,
                                               product_amortization__product__category=product_type)
    for exchange_amo in exchange_amos:
        revenue_count += exchange_amo.revenue_amount

    return revenue_count


def get_user_amortizations(user, product_type, settled_status):
    """获取用户还款计划"""

    user_amortizations = UserAmortization.objects.filter(user=user, settled=settled_status,
                                                         product_amortization__product__category=product_type
                                                         ).select_related(depth=2)

    return user_amortizations


def get_p2p_product_amounts(user, product_type):
    """获取用户购买的每个产品的投资额"""

    p2p_record = P2PRecord.objects.filter(user=user, product__category=product_type)
    p2p_amounts = p2p_record.values('product').annotate(Sum('amount'))
    return p2p_amounts


def classes_product_for_period(p_period):
    """根据产品期限分级"""

    class_name = None

    if p_period in range(1, 6):
        class_name = 'A'
    elif p_period == 6:
        class_name = 'B'
    elif p_period == 12:
        class_name = 'C'

    return class_name


# 类别名称
_CLASS = {
    'A': u'初级理财',
    'B': u'中极理财',
    'C': u'高级理财',
}


def get_class_name(p_class, l_type=None):
    """获取产品级别描述"""

    if l_type:
        class_name = _CLASS[p_class] + l_type
    else:
        class_name = _CLASS[p_class]

    return class_name


class RevenueExchangeIndexView(TemplateView):
    """
    理财收益兑换-产品视图
    :param 'type'
    :return
    :request_method GET
    :user.is_authenticated True
    """

    TYPES = {
        'fuel_card': (u'加油卡', 'fuel_index.jade'),
    }

    template_name = ''

    def get_context_data(self, e_type, **kwargs):
        l_type, template_name = self.TYPES.get(e_type, None)
        if not e_type or not l_type:
            return HttpResponseForbidden(u'type参数不存在')

        self.template_name = template_name
        user = self.request.user
        p2p_products = P2PProduct.objects.filter(hide=False, publish_time__lte=timezone.now(), category=l_type,
                                                 status=u'正在招标').order_by('period', '-priority')

        data = []
        if p2p_products:
            # 根据产品期限及优先级排序，然后获取每种期限的第一条记录
            data.append(p2p_products[0])
            unique_period = p2p_products[0].period
            for p2p_product in p2p_products[1:]:
                if p2p_product.period != unique_period:
                    data.append(p2p_product)
                    unique_period = p2p_product.period

            # 按产品期限分类（初级-中级-高级）
            for p in data:
                product_class = classes_product_for_period(p.period) or 'C'
                p.class_name = get_class_name(product_class, l_type)

        # 统计用户至今购买理财产品总收益
        revenue_count = get_user_revenue_count_for_type(user, l_type)

        # 统计生效中的理财产品份数
        effect_count = UserAmortization.objects.filter(user=user, settled=False,
                                                       product_amortization__product__category=l_type
                                                       ).count()

        return {
            'products': data,
            'revenue_count': revenue_count,
            'effect_count': effect_count,
        }


class RevenueExchangeBuyView(TemplateView):
    """
    理财收益兑换-产品购买页面视图
    :param 'p_id', 'type'
    :return
    :request_method GET
    :user.is_authenticated True
    """

    TYPES = {
        'fuel_card': (u'加油卡', 'fuel_buy.jade'),
    }

    template_name = ''

    def get_context_data(self, p_id, **kwargs):
        try:
            p2p_product = P2PProduct.objects.get(pk=p_id)
        except P2PProduct.DoesNotExist:
            return Http404(u'页面不存在')

        _type = self.request.GET.get('type', '').strip()
        l_type, template_name = self.TYPES.get(_type, None)
        if not _type or not l_type:
            return HttpResponseForbidden(u'type参数不存在')

        self.template_name = template_name

        # 获取产品期限
        product_period = p2p_product.period

        # 获取奖品使用范围
        using_range = get_p2p_reward_using_range(p2p_product.category)

        return {
            'product': p2p_product,
            'period': product_period,
            'using_range': using_range,
        }


class RevenueExchangeBuyApi(APIView):
    """
    理财收益兑换-产品购买接口
    :param 'p_id', 'p_parts', 'amount'
    :return
    :request_method POST
    :user.is_authenticated True
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if not request.user.wanglibaouserprofile.id_is_valid:
            return Response({
                'message': u'请先进行实名认证',
                'error_number': ErrorNumber.need_authentication
            }, status=status.HTTP_400_BAD_REQUEST)

        form = FuelCardBuyForm(data=request.POST)
        if form.is_valid():
            p2p_product = form.cleaned_data['p2p_product']
            p_parts = form.cleaned_data['p_parts']
            amount = form.cleaned_data['amount']
            exchange_rule = RevenueExchangeRule.objects.filter(product=p2p_product).first()

            # 判断用户是否满足最低消费限额
            if exchange_rule and exchange_rule.limit_min_per_user * p_parts == amount:
                try:
                    trader = P2PTrader(product=p2p_product, user=request.user, request=request)
                    product_info, margin_info, equity_info = trader.purchase(amount)

                    # 生成收益兑换订单
                    generate_revenue_exchange_order(request.user, p2p_product,
                                                    product_info.order_id, p_parts)

                    # FixMe, 补充短信内容，给用户发送投资成功短信通知
                    message = ''
                    messages_list = [message]
                    send_messages.apply_async(kwargs={
                        "phones": [request.user.wanglibaouserprofile.phone],
                        "messages": messages_list
                    })

                    return Response({
                        'data': product_info.amount,
                        'category': equity_info.product.category
                    })
                except Exception, e:
                    return Response({
                        'message': e.message,
                        'error_number': ErrorNumber.unknown_error
                    }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "message": form.errors,
                'error_number': ErrorNumber.form_error
            }, status=status.HTTP_400_BAD_REQUEST)


class RevenueExchangeBuyRecordView(TemplateView):
    """
    理财收益兑换-产品购买记录视图
    :param 'status', 'type'
    :return
    :request_method GET
    :user.is_authenticated True
    """

    TYPES = {
        'fuel_card': (u'加油卡', 'fuel_records_audit.jade'),
    }

    template_name = ''

    def _get_user_amortizations(self, user, product_type, settled_status, sorted_term):
        """获取用户还款计划"""

        user_amotization = get_user_amortizations(user, product_type, settled_status)
        user_amotization = user_amotization.order_by('product_amortization__product__id', sorted_term)

        ua_list = []
        ua_tmp = user_amotization.first()
        ua_list.append(ua_tmp)
        for ua in user_amotization:
            if ua.product_amortization.product != ua_tmp.product_amortization.product:
                ua_list.append(ua_tmp)
                ua_tmp = ua

        return get_sorts_for_created_time(ua_list)

    def get_context_data(self, **kwargs):
        _status = self.request.GET.get('status', '').strip()
        _type = self.request.GET.get('type', '').strip()

        if not _status:
            return HttpResponseForbidden(u'status参数是必须的')

        l_type, template_name = self.TYPES.get(_type, None)
        if not _type or not l_type:
            return HttpResponseForbidden(u'type参数不存在')

        self.template_name = template_name

        status_list = ['auditing', 'done']
        if _status in status_list:
            if _status == 'auditing':
                settled_status = False
                sorted_term = 'term'
            else:
                settled_status = True
                sorted_term = '-term'

            user_amortizations = self._get_user_amortizations(self.request.user, l_type, settled_status, sorted_term)

            # 按产品期限分类（初级-中级-高级）
            for ua in user_amortizations:
                product_class = classes_product_for_period(ua.product_amortization.product.period) or 'C'
                ua.class_name = get_class_name(product_class, l_type)

            return {
                'data': user_amortizations,
                'status': _status,
            }
        else:
            return HttpResponseForbidden(u'无效参数status')


class RevenueExchangeRecordView(TemplateView):
    """
    理财收益兑换-产品兑换记录视图
    :param 'status', 'type'
    :return
    :request_method GET
    :user.is_authenticated True
    """

    TYPES = {
        'fuel_card': (u'加油卡', 'fuel_records_exchange.jade'),
    }

    template_name = ''

    def get_context_data(self, **kwargs):
        _status = self.request.GET.get('status', '').strip()
        _type = self.request.GET.get('type', '').strip()
        if not _status:
            return HttpResponseForbidden(u'status参数是必须的')

        l_type, template_name = self.TYPES.get(_type, None)
        if not _type or not l_type:
            return HttpResponseForbidden(u'type参数不存在')

        self.template_name = template_name

        status_list = ['receiving', 'changing']
        if _status in status_list:
            exchang_status = False if _status == 'receiving' else True
            settled_status = False if _status == 'receiving' else True
            exchange_amos = ExchangeAmo.objects.filter(user=self.request.user, exchanged=exchang_status,
                                                       settled=settled_status,
                                                       product_amortization__product__category
                                                       =l_type).order_by('-term_date')
            if _status == 'changing':
                for ea in exchange_amos:
                    rewards = RevenueExchangeRepertory.objects.filter(user=self.request.user,
                                                                      order_id=ea.order_id,
                                                                      exchange_id=ea.exchange_id,
                                                                      is_used=False)
                    ea.reward = rewards

            # 按产品期限分类（初级-中级-高级）
            for ea in exchange_amos:
                product_class = classes_product_for_period(ea.product_amortization.product.period) or 'C'
                ea.class_name = get_class_name(product_class, l_type)

            return {
                'data': exchange_amos,
                'status': _status,
            }
        else:
            return HttpResponseForbidden(u'无效参数status')


class RevenueExchangeStatisticsView(TemplateView):
    """
    理财收益兑换-用户资金统计视图
    :param 'type'
    :return
    :request_method GET
    :user.is_authenticated True
    """

    template_name = ''

    TYPES = {
        'fuel_card': (u'加油卡', 'fuel_statistics.jade'),
    }

    class MyObject(object):
        pass

    def get_context_data(self, **kwargs):
        _type = self.request.GET.get('type', '').strip()

        l_type, template_name = self.TYPES.get(_type)
        if not _type or not l_type:
            return HttpResponseForbidden(u'type参数不存在')

        self.template_name = template_name
        user = self.request.user
        data = []

        # 获取用户注册时间
        register_time = user.date_joined

        revenue_count = Decimal('0.00')
        exchange_amos = ExchangeAmo.objects.filter(product_amortization__product__category=l_type,
                                                   user=user).order_by('product_amortization__product_period')
        if exchange_amos:
            unique_period = None
            for exchange_amo in exchange_amos:
                # 统计用户购标至今收益总额
                revenue_count += exchange_amo.revenue_amount

                # 获取用户每种等级产品的消费统计
                if exchange_amo.period != unique_period:
                    sub_exchange_amos = exchange_amos.filter(period=exchange_amo.period)
                    # 获取用户每产品购买份数
                    amo_count = sub_exchange_amos.count()
                    # 获取用户每产品已结算还款计划期数统计
                    exchanged_count = sub_exchange_amos.filter(exchanged=False).count()
                    # 获取用户每产品收益金额
                    revenue = exchange_amos.values('period').annotate(Sum('revenue_amount')).first()
                    revenue = revenue['revenue_amount__sum']

                    unique_period = exchange_amo
                    exchange_amo.total_revenue = revenue
                    exchange_amo.exchanged_count = exchanged_count
                    exchange_amo.buy_count = amo_count
                    data.append(exchange_amo)

            # 按产品期限分类(初级-中级-高级)
            for p2p_product in data:
                product_class = classes_product_for_period(p2p_product.period) or 'C'
                p2p_product.class_name = get_class_name(product_class, l_type)

        return {
            'data': data,
            'count': revenue_count,
            'register_time': register_time,
        }
