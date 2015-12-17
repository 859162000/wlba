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
from wanglibao_p2p.models import P2PProduct, UserAmortization
from wanglibao.const import ErrorNumber
from .forms import FuelCardBuyForm
from .trade import P2PTrader


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
                        # FixMe
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

    def get_sorts_for_created_time(self, queryset):
        """根据 created_time 对请求集排序（降序）"""

        data_list = sorted(queryset, key=lambda asd: asd.created_time, reverse=True)

        return data_list

    def get_user_amortizations(self, settled):
        """获取用户还款计划"""

        user_amotization = UserAmortization.objects.filter(user=self.request.user, settled=settled
                                                           ).select_related(depth=2)
        user_amotization = user_amotization.order_by('product_amortization__product_id', 'term')

        ua_list = []
        ua_tmp = user_amotization.first()
        ua_list.append(ua_tmp)
        for ua in user_amotization:
            if ua.product_amortization.product != ua_tmp.product_amortization.product:
                ua_list.append(ua_tmp)
                ua_tmp = ua

        return self.get_sorts_for_created_time(ua_list)

    def get_context_data(self, **kwargs):
        _status = self.request.GET.get('status', '').strip()
        if not _status:
            return HttpResponseForbidden(u'status参数不存在')

        status_list = ['auditing', 'done']
        if _status in status_list:
            settled = False if _status == 'auditing' else True
            data = self.get_user_amortizations(settled)

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

    template_name = 'fuel_records_exchange.jade'

    def get_sorts_for_created_time(self, queryset):
        """根据 created_time 对请求集排序（降序）"""

        data_list = sorted(queryset, key=lambda asd: asd.created_time, reverse=True)

        return data_list

    def get_user_amortizations(self, settled):
        """获取用户还款计划"""

        user_amotization = UserAmortization.objects.filter(user=self.request.user, settled=settled
                                                           ).select_related(depth=2)
        user_amotization = user_amotization.order_by('product_amortization__product_id', 'term')

        ua_list = []
        ua_tmp = user_amotization.first()
        ua_list.append(ua_tmp)
        for ua in user_amotization:
            if ua.product_amortization.product != ua_tmp.product_amortization.product:
                ua_list.append(ua_tmp)
                ua_tmp = ua

        return self.get_sorts_for_created_time(ua_list)

    def get_context_data(self, **kwargs):
        _status = self.request.GET.get('status', '').strip()
        if not _status:
            return HttpResponseForbidden(u'status参数不存在')

        status_list = ['wait_receive', 'receive']
        if _status in status_list:
            settled = False if _status == 'wait_receive' else True
            data = self.get_user_amortizations(settled)


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

        return {
            'p2p_product': p2p_product,
            'phone': phone,
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

        data = []
        if p2p_products:
            # 根据优先级排序，并获取每种优先级的第一条记录
            data.append(p2p_products[0])
            unique_priority = p2p_products[0].priority
            for p2p_product in p2p_products[1:]:
                if p2p_product.priority != unique_priority:
                    data.append(p2p_product)
                    unique_priority = p2p_product.priority

        return {
            'html_data': data,
        }
