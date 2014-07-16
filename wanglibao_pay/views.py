# -*- coding: utf-8 -*-
import logging
import socket
import datetime
from django.db import transaction
from django.forms import model_to_dict
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from order.models import Order
from order.utils import OrderHelper
from wanglibao_margin.exceptions import MarginLack
from wanglibao_margin.marginkeeper import MarginKeeper
from wanglibao_pay.models import Bank, Card, PayResult
from wanglibao_pay.huifu_pay import HuifuPay, SignException
from wanglibao_pay.models import PayInfo
import decimal
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from wanglibao_pay.serializers import CardSerializer
from wanglibao_pay.util import get_client_ip

logger = logging.getLogger(__name__)
TWO_PLACES = decimal.Decimal(10) ** -2


class BankListView(TemplateView):
    template_name = 'pay_banks.jade'

    def get_context_data(self, **kwargs):
        return {
            'banks': Bank.get_deposit_banks()
        }


class PayView(TemplateView):
    template_name = 'pay_jump.jade'

    def post(self, request):
        form = dict()
        message = ''
        try:
            amount_str = request.POST.get('amount', '')
            amount = decimal.Decimal(amount_str).\
                quantize(TWO_PLACES, context=decimal.Context(traps=[decimal.Inexact]))
            amount_str = str(amount)
            if amount <= 0:
                raise decimal.DecimalException()

            gate_id = request.POST.get('gate_id', '')
            bank = Bank.objects.get(gate_id=gate_id)

            pay_info = PayInfo()
            pay_info.amount = amount
            pay_info.total_amount = amount
            pay_info.type = PayInfo.DEPOSIT
            pay_info.status = PayInfo.INITIAL
            pay_info.user = request.user
            pay_info.bank = bank
            pay_info.request_ip = get_client_ip(request)

            order = OrderHelper.place_order(request.user, Order.PAY_ORDER, pay_info.status,
                                            pay_info=model_to_dict(pay_info))
            pay_info.order = order
            pay_info.save()

            post = {
                'OrdId': pay_info.pk,
                'GateId': gate_id,
                'OrdAmt': amount_str
            }
            pay = HuifuPay()
            form = pay.pay(post)
            pay_info.request = str(form)
            pay_info.status = PayInfo.PROCESSING
            pay_info.save()
            OrderHelper.update_order(order, request.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
        except decimal.DecimalException:
            message = u'金额格式错误'
        except Bank.DoesNotExist:
            message = u'请选择有效的银行'
        except (socket.error, SignException) as e:
            message = PayResult.RETRY
            pay_info.status = PayInfo.FAIL
            pay_info.error_message = str(e)
            pay_info.save()
            OrderHelper.update_order(order, request.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
            logger.fatal('sign error! order id: ' + str(pay_info.pk) + ' ' + str(e))

        context = {
            'message': message,
            'form': form
        }
        return self.render_to_response(context)


class PayCompleteView(TemplateView):
    template_name = 'pay_complete.jade'

    def post(self, request, *args, **kwargs):
        result = HuifuPay.handle_pay_result(request)
        amount = request.POST.get('OrdAmt', '')
        return self.render_to_response({
            'result': result,
            'amount': amount
        })

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(PayCompleteView, self).dispatch(request, *args, **kwargs)


class PayCallback(View):
    def post(self, request, *args, **kwargs):
        HuifuPay.handle_pay_result(request)
        order_id = request.POST.get('OrdId', '')
        return HttpResponse('RECV_ORD_ID_' + order_id)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(PayCallback, self).dispatch(request, *args, **kwargs)


class WithdrawView(TemplateView):
    template_name = 'withdraw.jade'

    def get_context_data(self, **kwargs):
        cards = Card.objects.filter(user=self.request.user).select_related()
        banks = Bank.get_withdraw_banks()
        return {
            'cards': cards,
            'banks': banks,
            'user_profile': self.request.user.wanglibaouserprofile,
            'margin': self.request.user.margin.margin,
            'fee': HuifuPay.FEE
        }


class WithdrawCompleteView(TemplateView):
    template_name = 'withdraw_complete.jade'

    @method_decorator(transaction.atomic)
    def post(self, request, *args, **kwargs):
        if not request.user.wanglibaouserprofile.id_is_valid:
            return self.render_to_response({
                'result': u'请先进行实名认证'
            })

        result = PayResult.WITHDRAW_SUCCESS
        try:
            amount_str = request.POST.get('amount', '')
            amount = decimal.Decimal(amount_str). \
                quantize(TWO_PLACES, context=decimal.Context(traps=[decimal.Inexact]))
            if amount <= 0:
                raise decimal.DecimalException

            fee = (amount * HuifuPay.FEE).quantize(TWO_PLACES)
            actual_amount = amount - fee

            card_id = request.POST.get('card_id', '')
            card = Card.objects.get(pk=card_id)

            pay_info = PayInfo()
            pay_info.amount = actual_amount
            pay_info.fee = fee
            pay_info.total_amount = amount
            pay_info.type = PayInfo.WITHDRAW
            pay_info.user = request.user
            pay_info.card_no = card.no
            pay_info.account_name = request.user.wanglibaouserprofile.name
            pay_info.bank = card.bank
            pay_info.request_ip = get_client_ip(request)
            pay_info.status = PayInfo.ACCEPTED

            order = OrderHelper.place_order(request.user, Order.WITHDRAW_ORDER, pay_info.status,
                                            pay_info=model_to_dict(pay_info))
            pay_info.order = order
            keeper = MarginKeeper(request.user, pay_info.order.pk)
            margin_record = keeper.withdraw_pre_freeze(amount)
            pay_info.margin_record = margin_record

            pay_info.save()
        except decimal.DecimalException:
            result = u'金额格式错误'
        except Card.DoesNotExist:
            result = u'请选择有效的银行卡'
        except MarginLack as e:
            result = u'余额不足'
            pay_info.error_message = str(e)
            pay_info.status = PayInfo.FAIL
            pay_info.save()

        return self.render_to_response({
            'result': result
        })


class WithdrawCallback(View):
    def post(self, request, *args, **kwargs):
        HuifuPay.handle_withdraw_result(request.POST.dict())
        order_id = request.POST.get('OrdId', '')
        return HttpResponse('RECV_ORD_ID_' + order_id)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(WithdrawCallback, self).dispatch(request, *args, **kwargs)


class CardViewSet(ModelViewSet):
    model = Card
    serializer = CardSerializer
    throttle_classes = (UserRateThrottle,)
    permission_classes = IsAuthenticated,

    @property
    def allowed_methods(self):
        return 'POST'

    def create(self, request):
        card = Card()
        card.user = request.user
        card.no = request.DATA.get('no', '')
        bank_id = request.DATA.get('bank', '')
        card.bank = Bank.objects.get(pk=bank_id)
        card.save()

        return Response({
            'id': card.pk,
            'no': card.no,
            'bank_name': card.bank.name
        })


class WithdrawTransactions(TemplateView):
    template_name = 'withdraw_transactions.jade'
    COB_HOUR = 15

    def get_context_data(self, **kwargs):
        now = datetime.datetime.now()
        end = datetime.datetime(now.year, now.month, now.day, WithdrawTransactions.COB_HOUR)
        if now.hour < WithdrawTransactions.COB_HOUR:
            end = end - datetime.timedelta(days=1)
        start = end - datetime.timedelta(days=1)

        trade_records = PayInfo.objects.filter(update_time__gte=start, update_time__lt=end, status=PayInfo.ACCEPTED,
                                               type=PayInfo.WITHDRAW)
        return {
            "trade_records": trade_records
        }

