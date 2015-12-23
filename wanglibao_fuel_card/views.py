# coding=utf-8

import logging
from django.utils import timezone
from django.views.generic import TemplateView
from django.shortcuts import render_to_response
from django.http import HttpResponseForbidden
from django.db.models import Sum
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from wanglibao_account.cooperation import get_phone_for_coop
from wanglibao_p2p.models import P2PProduct, UserAmortization, P2PRecord
from wanglibao.const import ErrorNumber
from wanglibao_sms.tasks import send_messages
from marketing.models import P2PRewardRecord
from .forms import FuelCardBuyForm
from .trade import P2PTrader
from .utils import get_sorts_for_created_time, get_p2p_reward_using_range

logger = logging.getLogger(__name__)


def get_user_revenue_count_for_type(user, product_type):
    """根据产品类型获取用户自注册起至今总收益"""

    revenue_count = 0
    p2p_record_list = P2PRecord.objects.filter(user=user, product__category=product_type)
    for p2p_record in p2p_record_list:
        p2p_amount = float(p2p_record.amount)
        p2p_parts = p2p_amount / p2p_record.product.limit_min_per_user
        p2p_reward_count = p2p_parts * p2p_record.product.equality_prize_amount
        p2p_revenue = p2p_reward_count - p2p_amount
        revenue_count += p2p_revenue

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


# 加油卡类别名称
FUEL_CARD_CLASS = {
    'A': u'初级理财加油卡',
    'B': u'中极理财加油卡',
    'C': u'高级理财加油卡',
}


class FuelCardIndexView(TemplateView):
    """
    APP加油卡产品购买列表展示
    :param
    :return
    :request_method GET
    :user.is_authenticated True
    """

    template_name = 'fuel_index.jade'


    def get_context_data(self, **kwargs):
        user = self.request.user
        p2p_products = P2PProduct.objects.filter(hide=False, publish_time__lte=timezone.now(), category=u'加油卡',
                                                 status=u'正在招标').order_by('period', '-priority')

        data = []
        product_1 = product_2 = product_3 = None
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
                p.class_name = FUEL_CARD_CLASS[product_class]

        # 获取用户手机号(屏蔽)
        phone = get_phone_for_coop(user.id)

        # 获取用户至今总收益
        revenue_count = get_user_revenue_count_for_type(user, u'加油卡')

        effect_count = get_user_amortizations(user, u'加油卡', False).count()

        return {
            'products': data,
            'phone': phone,
            'revenue_count': revenue_count,
            'effect_count': effect_count,
        }


class FuelCardBuyView(TemplateView):
    """
    加油卡购买页面视图
    :param
    :return
    :request_method GET
    :user.is_authenticated True
    """

    template_name = 'fuel_buy.jade'

    def get_context_data(self, p_id, **kwargs):
        user = self.request.user

        try:
            p2p_product = P2PProduct.objects.get(pk=p_id)
        except P2PProduct.DoesNotExist:
            return HttpResponseForbidden(u'无效产品ID')

        # 获取产品期限
        product_period = p2p_product.period

        # 获取奖品使用范围
        # FixMe, 优化设计==>修改奖品使用范围设计，建议单独分离到一张表中
        using_range = get_p2p_reward_using_range(p2p_product.category)

        # 获取用户手机号(屏蔽)
        phone = get_phone_for_coop(user.id)

        return {
            'product': p2p_product,
            'period': product_period,
            'using_range': using_range,
            'phone': phone,
        }


class FuelCardBuyApi(APIView):
    """
    加油卡购买接口
    :param 'p_id', 'p_parts', 'amount', 'reward_range'
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
            reward_range = form.cleaned_data['reward_range']
            # 判断用户是否满足最低消费限额
            if p2p_product.limit_min_per_user * p_parts == amount:
                try:
                    trader = P2PTrader(product=p2p_product, user=request.user, request=request)
                    product_info, margin_info, equity_info = trader.purchase(amount)

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


class FuelCardBugRecordView(TemplateView):
    """
    加油卡购买记录视图
    :param
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
                ua.class_name = FUEL_CARD_CLASS[product_class]

            return {
                'data': user_amortizations,
                'status': _status,
            }
        else:
            return HttpResponseForbidden(u'无效参数status')


class FuelCardExchangeRecordView(TemplateView):
    """
    加油卡兑换记录视图
    :param
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

        status_list = ['wait_receive', 'receive']
        if _status in status_list:
            settled_status = False if _status == 'wait_receive' else True
            user_amortizations = get_user_amortizations(self.request.ser,
                                                        settled_status,
                                                        _type).order_by('-term_date')
            if _status == 'receive':
                for ua in user_amortizations:
                    p2p_reward_record = P2PRewardRecord.objects.get(user=self.request.user,
                                                                    order_id=ua.product_amortization.order_id)
                    ua.reward = p2p_reward_record.reward

            # 按产品期限分类（初级-中级-高级）
            for ua in user_amortizations:
                product_class = classes_product_for_period(ua.product_amortization.product.period) or 'C'
                ua.class_name = FUEL_CARD_CLASS[product_class]

            return {
                'data': user_amortizations,
                'status': _status,
            }
        else:
            return HttpResponseForbidden(u'无效参数status')


class FualCardStatisticsView(TemplateView):
    """
    加油卡资金统计
    :param
    :return
    :request_method GET
    :user.is_authenticated True
    """

    template_name = ''

    TYPES = {
        'fuel_card': (u'加油卡', 'fuel_statistics.jade'),
    }

    def get_user_amortizations(self, user, product, settled_status):
        """获取用户还款计划"""

        user_amortizations = UserAmortization.objects.filter(user=user, settled=settled_status,
                                                             product_amortization__product=product
                                                             ).select_related(depth=2)

        return user_amortizations

    def get_context_data(self, **kwargs):
        _type = self.request.GET.get('type', '').strip()

        l_type, template_name = self.TYPES.get(_type)
        if not _type or not l_type:
            return HttpResponseForbidden(u'type参数不存在')

        self.template_name = template_name
        user = self.request.user

        # 获取用户购标至今节省总金额
        total_revenue = get_user_revenue_count_for_type(user, l_type)

        # 获取用户注册时间
        register_time = user.date_joined

        # 获取用户资金统计
        data = []
        user_amounts = get_p2p_product_amounts(user, l_type).order_by('-create_time')
        for ua in user_amounts:
            try:
                p2p_product = P2PProduct.objects.get(pk=ua['product'])
            except P2PProduct.DoesNotExist:
                logger.error('user[%s] amount count faild product[%s] does not exists' % (user.id, ua['product']))
                return Response({}, status=status.HTTP_400_BAD_REQUEST)

            # 获取用户每产品购买份数
            p2p_parts = float(ua['amount__sum']) / p2p_product.limit_min_per_user

            # 获取用户每产品收益金额
            offset_revenue = p2p_product.limit_min_per_user - p2p_product.equality_prize_amount
            revenue = p2p_parts * offset_revenue

            # 获取用户每产品已结算还款计划期数统计
            settled_count = get_user_amortizations(user, p2p_product, True).count()

            p2p_product.parts = p2p_parts
            p2p_product.revenue = revenue
            p2p_product.settled_count = settled_count

            data.append(p2p_product)

        # 按产品期限分类(初级-中级-高级)
        for p2p_product in data:
            product_class = classes_product_for_period(p2p_product.period) or 'C'
            p2p_product.class_name = FUEL_CARD_CLASS[product_class]

        return {
            'data': data,
            'count': total_revenue,
            'register_time': register_time,
        }
