# -*- coding: utf-8 -*-
import logging
import socket
from django.db import transaction
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet
from order.utils import OrderHelper
from wanglibao_margin.exceptions import MarginLack
from wanglibao_margin.marginkeeper import MarginKeeper
from wanglibao_pay.models import Bank, Card
from wanglibao_pay.huifu_pay import HuifuPay, SignException
from wanglibao_pay.models import PayInfo
import requests
import xml.etree.ElementTree as ET
import decimal

from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from wanglibao_pay.serializers import CardSerializer

logger = logging.getLogger(__name__)
TWO_PLACES = decimal.Decimal(10) ** -2


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class BankListView(TemplateView):
    template_name = 'pay_banks.jade'

    def get_context_data(self, **kwargs):
        return {
            'banks': Bank.objects.all(),
        }


class PayResult(object):
    DEPOSIT_SUCCESS = u'充值成功'
    DEPOSIT_FAIL = u'充值失败'
    WITHDRAW_SUCCESS = u'提现成功'
    WITHDRAW_FAIL = u'提现失败'
    RETRY = u'系统内部错误，请重试'
    EXCEPTION = u'系统内部错误，请联系客服'


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
            Bank.objects.get(gate_id=gate_id)

            order = OrderHelper().place_order(request.user)
            pay_info = PayInfo()
            pay_info.order = order
            pay_info.amount = amount
            pay_info.type = PayInfo.DEPOSIT
            pay_info.status = PayInfo.INITIAL
            pay_info.user = request.user
            pay_info.save()

            post = {
                'OrdId': pay_info.pk,
                'GateId': gate_id,
                'OrdAmt': amount_str
            }
            pay = HuifuPay()
            form = pay.pay(post)
            pay_info.request = str(form)
            pay_info.request_ip = get_client_ip(request)
            pay_info.status = PayInfo.PROCESSING
            pay_info.save()
        except decimal.DecimalException:
            message = u'金额格式错误'
        except Bank.DoesNotExist:
            message = u'请选择有效的银行'
        except (socket.error, SignException) as e:
            message = PayResult.RETRY
            pay_info.status = PayInfo.FAIL
            pay_info.error_message = str(e)
            pay_info.save()
            logger.fatal('sign error! order id: ' + str(pay_info.pk) + ' ' + str(e))

        context = {
            'message': message,
            'form': form
        }
        return self.render_to_response(context)


@transaction.atomic
def handle_pay_result(request):
    order_id = request.POST.get('OrdId', '')
    try:
        pay_info = PayInfo.objects.select_for_update().get(pk=order_id)
    except PayInfo.DoesNotExist:
        logger.warning('Order not found, order id: ' + order_id + ', response: ' + request.body)
        return PayResult.EXCEPTION

    if pay_info.status == PayInfo.SUCCESS:
        return PayResult.DEPOSIT_SUCCESS

    amount = request.POST.get('OrdAmt', '')
    code = request.POST.get('RespCode', '')
    message = request.POST.get('ErrMsg', '')
    pay_info.error_code = code
    pay_info.error_message = message
    pay_info.response = request.body
    pay_info.response_ip = get_client_ip(request)

    result = u''
    try:
        pay = HuifuPay()
        if pay.verify_sign(request.POST.dict(), HuifuPay.PAY_FIELDS):
            if pay_info.amount != decimal.Decimal(amount):
                pay_info.status = PayInfo.FAIL
                pay_info.error_message += u' 金额不匹配'
                logger.error('Amount mismatch, order id: %s request amount: %f response amount: %s',
                             order_id, float(pay_info.amount), amount)
                result = PayResult.EXCEPTION
            else:
                if code == '000000':
                    keeper = MarginKeeper(request.user, pay_info.order.pk)
                    keeper.deposit(amount)
                    pay_info.status = PayInfo.SUCCESS
                    result = PayResult.DEPOSIT_SUCCESS
                else:
                    pay_info.status = PayInfo.FAIL
                    result = PayResult.DEPOSIT_FAIL
        else:
            pay_info.error_message = 'Invalid signature. Order id: ' + order_id
            logger.error(pay_info.error_message)
            pay_info.status = PayInfo.EXCEPTION
            result = PayResult.EXCEPTION
    except (socket.error, SignException) as e:
        pay_info.error_message = str(e)
        pay_info.status = PayInfo.EXCEPTION
        logger.fatal('sign error! order id: ' + order_id + ' ' + str(e))
        result = PayResult.EXCEPTION

    pay_info.save()
    return result


class PayCompleteView(TemplateView):
    template_name = 'pay_complete.jade'

    def post(self, request, *args, **kwargs):
        result = handle_pay_result(request)
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
        handle_pay_result(request)
        order_id = request.POST.get('OrdId', '')
        return HttpResponse('RECV_ORD_ID_' + order_id)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(PayCallback, self).dispatch(request, *args, **kwargs)


class WithdrawView(TemplateView):
    template_name = 'withdraw.jade'

    def get_context_data(self, **kwargs):
        cards = Card.objects.filter(user=self.request.user).select_related()
        banks = Bank.objects.all()
        return {
            'cards': cards,
            'banks': banks,
            'user_profile': self.request.user.wanglibaouserprofile,
            'margin': self.request.user.margin.margin,
            'fee': HuifuPay.FEE
        }


@transaction.atomic
def handle_withdraw_result(data):
    order_id = data.get('OrdId', '')
    try:
        pay_info = PayInfo.objects.select_for_update().get(pk=order_id)
    except PayInfo.DoesNotExist:
        logger.warning('Order not found, order id: ' + order_id + ', response: ' + str(data))
        return PayResult.EXCEPTION

    if pay_info.status == PayInfo.FAIL:
        return PayResult.WITHDRAW_FAIL

    pay_info = PayInfo.objects.select_for_update().get(pk=order_id)
    pay_info.response = str(data)
    pay_info.error_code = data.get('RespCode', '')
    pay_info.error_message = data.get('RespDesc', '')
    transaction_status = data.get('TransStat', '')

    keeper = MarginKeeper(pay_info.user, pay_info.order.pk)

    try:
        pay = HuifuPay()
        if pay.verify_sign(data, HuifuPay.WITHDRAW_FIELDS):
            if data['RespCode'] == '000':
                if transaction_status == 'S':
                    if pay_info.status != PayInfo.SUCCESS:
                        keeper.withdraw_ack(pay_info.amount)
                    pay_info.status = PayInfo.SUCCESS
                    result = PayResult.WITHDRAW_SUCCESS
                elif transaction_status == 'I':
                    pay_info.status = PayInfo.ACCEPTED
                    result = PayResult.WITHDRAW_SUCCESS
                else:
                    pay_info.status = PayInfo.FAIL
                    result = PayResult.WITHDRAW_FAIL
                    keeper.withdraw_rollback(pay_info.amount)
            else:
                pay_info.status = PayInfo.FAIL
                result = PayResult.WITHDRAW_FAIL
                keeper.withdraw_rollback(pay_info.amount)
        else:
            pay_info.status = PayInfo.EXCEPTION
            result = PayResult.EXCEPTION
            pay_info.error_message = 'Invalid signature'
            logger.fatal('invalid signature. order id: %s', str(pay_info.pk))
    except(socket.error, SignException) as e:
        result = PayResult.EXCEPTION
        pay_info.status = PayInfo.EXCEPTION
        pay_info.error_message = str(e)
        logger.fatal('unexpected error. order id: %s. exception: %s', str(pay_info.pk), str(e))

    pay_info.save()
    return result


class WithdrawCompleteView(TemplateView):
    template_name = 'withdraw_complete.jade'

    def post(self, request, *args, **kwargs):
        if not request.user.wanglibaouserprofile.id_is_valid:
            return self.render_to_response({
                'result': u'请先进行实名认证'
            })

        result = u''
        try:
            amount_str = request.POST.get('amount', '')
            amount = decimal.Decimal(amount_str). \
                quantize(TWO_PLACES, context=decimal.Context(traps=[decimal.Inexact]))
            amount_str = str(amount)
            if amount <= 0:
                raise decimal.DecimalException

            fee = (amount * HuifuPay.FEE).quantize(TWO_PLACES)
            actual_amount = amount - fee

            card_id = request.POST.get('card_id', '')
            card = Card.objects.get(pk=card_id)

            order = OrderHelper.place_order(request.user)
            pay_info = PayInfo()
            pay_info.order = order
            pay_info.amount = actual_amount
            pay_info.fee = fee
            pay_info.total_amount = amount
            pay_info.type = PayInfo.WITHDRAW
            pay_info.user = request.user
            pay_info.status = PayInfo.INITIAL
            pay_info.save()

            keeper = MarginKeeper(request.user, pay_info.order.pk)
            keeper.withdraw_pre_freeze(amount)

            post = dict()
            post['OrdId'] = str(pay_info.pk)
            post['OrdAmt'] = actual_amount
            post['AcctName'] = request.user.wanglibaouserprofile.name
            post['BankId'] = card.bank.code
            post['AcctId'] = card.no
            post['PrPurpose'] = 'p2p'

            pay = HuifuPay()
            form = pay.withdraw(post)

            pay_info.request = unicode(form)
            pay_info.request_ip = get_client_ip(request)
            pay_info.status = PayInfo.PROCESSING
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
        except (socket.error, SignException) as e:
            result = PayResult.EXCEPTION
            pay_info.error_message = str(e)
            pay_info.status = PayInfo.FAIL
            pay_info.save()
            keeper.withdraw_rollback(amount)
            logger.fatal('sign error! order id: ' + str(pay_info.pk) + ' ' + str(e))

        if result:
            return self.render_to_response({
                'result': result
            })

        try:
            r = requests.post(form['url'], form['post'])
            root = ET.fromstring(r.text.encode('utf-8'))
            ret = root.find('result')
            data = dict()
            for child in ret:
                data[child.tag] = child.text
        except requests.exceptions.ConnectionError as e:
            result = PayResult.WITHDRAW_FAIL
            pay_info.status = PayInfo.FAIL
            pay_info.error_message = str(e)
            pay_info.save()
            keeper.withdraw_rollback(amount)
            logger.error('connection error. order id: %s. exception: %s', str(pay_info.pk), str(e))
        except (requests.exceptions.HTTPError, requests.exceptions.Timeout, ET.ParseError) as e:
            result = PayResult.EXCEPTION
            pay_info.status = PayInfo.EXCEPTION
            pay_info.error_message = str(e)
            pay_info.save()
            logger.fatal('unexpected error. order id: %s. exception: %s', str(pay_info.pk), str(e))

        if result:
            return self.render_to_response({
                'result': result
            })

        result = handle_withdraw_result(data)
        return self.render_to_response({
            'result': result,
            'amount': amount
        })


class WithdrawCallback(View):
    def post(self, request, *args, **kwargs):
        handle_withdraw_result(request.POST.dict())
        order_id = request.POST.get('OrdId', '')
        return HttpResponse('RECV_ORD_ID_' + order_id)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(WithdrawCallback, self).dispatch(request, *args, **kwargs)


class CardViewSet(ModelViewSet):
    model = Card
    serializer = CardSerializer
    throttle_classes = (UserRateThrottle,)
    permission_classes = IsAdminUser,

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

