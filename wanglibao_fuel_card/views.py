# coding=utf-8

from django.utils import timezone
from django.views.generic import TemplateView
from django.shortcuts import render_to_response
from django.http import HttpResponseForbidden
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from wanglibao_account.cooperation import get_phone_for_coop
from wanglibao_p2p.models import P2PProduct, UserAmortization, P2PRecord
from wanglibao.const import ErrorNumber
from marketing.models import P2PRewardRecord
from .forms import FuelCardBuyForm
from .trade import P2PTrader
from .utils import get_sorts_for_created_time, get_p2p_reward_using_range


class FuelCardBuyApi(APIView):
    """
    加油卡购买接口
    :param
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
            total_amount = form.cleaned_data['total_amount']
            # 判断用户是否满足最低消费限额
            if p2p_product.limit_min_per_user * p_parts == total_amount:
                try:
                    trader = P2PTrader(product=p2p_product, user=request.user, request=request)
                    product_info, margin_info, equity_info = trader.purchase(total_amount)

                    return render_to_response('', {
                        # FixMe, 返回内容协商, 给用户发送投资成功短信通知
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

    template_name = 'fuel_records_audit.jade'

    def get_user_amortizations(self, settled_status):
        """获取用户还款计划"""

        user_amotization = UserAmortization.objects.filter(user=self.request.user, settled=settled_status,
                                                           product_amortization__product_category=u'加油卡'
                                                           ).select_related(depth=2)
        user_amotization = user_amotization.order_by('product_amortization__product_id', 'term')

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
        if not _status:
            return HttpResponseForbidden(u'status参数不存在')

        status_list = ['auditing', 'done']
        if _status in status_list:
            settled_status = False if _status == 'auditing' else True
            data = self.get_user_amortizations(settled_status)

            return {
                'data': data,
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
    """

    TYPES = {
        'fuel_card': (u'加油卡', 'fuel_records_exchange.jade'),
    }

    template_name = ''

    def get_user_amortizations(self, user, settled_status, _type):
        """获取用户还款计划"""

        user_amortizations = UserAmortization.objects.filter(user=user, settled=settled_status,
                                                             product_amortization__product_category=_type
                                                             ).select_related(depth=2).order_by('-term_date')

        return user_amortizations

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
            data = []
            settled_status = False if _status == 'wait_receive' else True
            user_amortizations = self.get_user_amortizations(self.request.user, settled_status, l_type)
            if _status == 'receive':
                for ua in user_amortizations:
                    p2p_reward_record = P2PRewardRecord.objects.get(user=self.request.user,
                                                                    order_id=ua.product_amortization.order_id)
                    data.append((ua, p2p_reward_record.reward,))
            else:
                data = user_amortizations or []

            return {
                'data': data,
                'status': _status,
            }
        else:
            return HttpResponseForbidden(u'无效参数status')


class FuelCardBuyView(TemplateView):
    """
    加油卡购买页面视图
    :param
    :return
    :request_method GET
    """

    template_name = 'fuel_buy.jade'

    def get_context_data(self, p_id, **kwargs):
        phone = get_phone_for_coop(self.request.user.id)
        try:
            p2p_product = P2PProduct.objects.get(pk=p_id)
        except P2PProduct.DoesNotExist:
            return HttpResponseForbidden(u'无效产品ID')

        using_range = get_p2p_reward_using_range(self.request.user.id, p2p_product.category,
                                                 p2p_product.equality_prize_amount)

        return {
            'p2p_product': p2p_product,
            'phone': phone,
            'using_range': using_range,
        }


class FuelCardListViewForApp(TemplateView):
    """
    APP加油卡产品购买列表展示
    :param
    :return
    :request_method GET
    """

    template_name = 'fuel_index.jade'

    def get_context_data(self, **kwargs):
        # 优先级越低排越前面
        p2p_products = P2PProduct.objects.filter(hide=False, publish_time__lte=timezone.now(), category=u'加油卡',
                                                 status__in=[u'已完成', u'满标待打款', u'满标已打款', u'满标待审核',
                                                             u'满标已审核', u'还款中', u'正在招标'
                                                             ]).order_by('priority', '-publish_time')

        product_data = []
        if p2p_products:
            # 根据优先级排序，并获取每种优先级的第一条记录
            product_data.append(p2p_products[0])
            unique_priority = p2p_products[0].priority
            for p2p_product in p2p_products[1:]:
                if p2p_product.priority != unique_priority:
                    product_data.append(p2p_product)
                    unique_priority = p2p_product.priority
        print len(product_data)
        return {
            'products': product_data,
        }


class FualCardAccountView(TemplateView):
    """加油卡资金统计"""

    template_name = ''

    TYPES = {
        'fuel_card': (u'加油卡', 'fuel_account.jade'),
    }

    def get_user_amortizations(self):
        """获取用户还款计划"""

        user_amotization = UserAmortization.objects.filter(user=self.request.user, settled=True,
                                                           product_amortization__product_category=u'加油卡'
                                                           ).select_related(depth=2)
        user_amotization = user_amotization.order_by('product_amortization__product_id', '-term')

        ua_list = []
        ua_tmp = user_amotization.first()
        ua_list.append(ua_tmp)
        for ua in user_amotization:
            if ua.product_amortization.product != ua_tmp.product_amortization.product:
                ua_list.append(ua_tmp)
                ua_tmp = ua

        return get_sorts_for_created_time(ua_list)

    def get_context_data(self, **kwargs):
        _type = self.request.GET.get('type', '').strip()

        l_type, template_name = self.TYPES.get(_type)
        if not _type or not l_type:
            return HttpResponseForbidden(u'type参数不存在')

        self.template_name = template_name
        user = self.request.user

        total_revenue = 0
        register_time = user.date_joined
        user_amortizations = self.get_user_amortizations()
        for ua in user_amortizations:
            product = ua.product_amortization.product
            p2p_parts = product.amount / product.limit_min_per_user
            p2p_offset_amount = product.equality_prize_amount - product.limit_min_per_user
            per_p2p_revenue = p2p_parts * p2p_offset_amount
            total_revenue += per_p2p_revenue

        return {
            'data': user_amortizations or [],
            'count': total_revenue,
            'register_time': register_time,
        }
