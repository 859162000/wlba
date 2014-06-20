# -*- coding: utf-8 -*-
import logging
import socket
from django.db import transaction
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View
from wanglibao_p2p.trade import UserMarginManager
from wanglibao_pay.models import Bank, Card
from wanglibao_pay.huifu_pay import HuifuPay, SignException
from wanglibao_pay.models import PayInfo
import requests
import xml.etree.ElementTree as ET
import decimal

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

            gate_id = request.POST.get('gate_id', '')
            Bank.objects.get(gate_id=gate_id)

            pay_info = PayInfo()
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
            message = u'系统内部错误,请重试'
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
        return u'系统内部错误，请联系客服'

    if pay_info.status == PayInfo.SUCCESS:
        return u'充值成功'

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
                result = u'系统内部错误，请联系客服'
            else:
                if code == '000000':
                    #user_margin = UserMarginManager(request.user)
                    #user_margin.deposit(amount)
                    pay_info.status = PayInfo.SUCCESS
                    result = u'充值成功'
                else:
                    pay_info.status = PayInfo.FAIL
                    result = u'充值失败'
        else:
            pay_info.error_message = 'Invalid signature. Order id: ' + order_id
            logger.error(pay_info.error_message)
            pay_info.status = PayInfo.EXCEPTION
    except (socket.error, SignException) as e:
        pay_info.error_message = str(e)
        pay_info.status = PayInfo.EXCEPTION
        logger.fatal('sign error! order id: ' + order_id + ' ' + str(e))

    pay_info.save()
    return result


class PayCompleteView(TemplateView):
    template_name = 'pay_complete.jade'

    def post(self, request, *args, **kwargs):
        result = handle_pay_result(request)
        return self.render_to_response({
            'result': result
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
        return {
            'cards': cards,
            'user_profile': self.request.user.wanglibaouserprofile
        }


@transaction.atomic
def handle_withdraw_result(data, user):
    order_id = data.get('OrdId', '')
    try:
        pay_info = PayInfo.objects.select_for_update().get(pk=order_id)
    except PayInfo.DoesNotExist:
        logger.warning('Order not found, order id: ' + order_id + ', response: ' + str(data))
        return u'系统内部错误,请联系客服人员'

    if pay_info.status == PayInfo.FAIL:
        return u'提款失败'

    pay_info = PayInfo.objects.select_for_update().get(pk=order_id)
    pay_info.response = str(data)
    pay_info.error_code = data.get('RespCode', '')
    pay_info.error_message = data.get('RespDesc', '')
    transaction_status = data.get('TransStat', '')

    user_margin = UserMarginManager(user)

    try:
        pay = HuifuPay()
        if pay.verify_sign(data, HuifuPay.WITHDRAW_FIELDS):
            if data['RespCode'] == '000':
                if transaction_status == 'S':
                    pay_info.status = PayInfo.SUCCESS
                    result = u'提款成功'
                elif transaction_status == 'I':
                    pay_info.status = PayInfo.ACCEPTED
                    result = u'银行已受理'
                else:
                    pay_info.status = PayInfo.FAIL
                    result = u'提款失败'
                    user_margin.unfreeze(pay_info.amount)
            else:
                pay_info.status = PayInfo.FAIL
                result = u'提款失败'
                user_margin.unfreeze(pay_info.amount)
        else:
            pay_info.status = PayInfo.EXCEPTION
            pay_info.error_message = 'Invalid signature'
            result = u'系统内部错误,请联系客服人员'
            logger.fatal('invalid signature. order id: %s', str(pay_info.pk))
    except(socket.error, SignException) as e:
        result = u'系统内部错误,请联系客服人员'
        pay_info.status = PayInfo.EXCEPTION
        pay_info.error_message = str(e)
        logger.fatal('unexpected error. order id: %s. exception: %s', str(pay_info.pk), str(e))

    pay_info.save()
    return result


class WithdrawCompleteView(TemplateView):
    template_name = 'withdraw_complete.jade'

    def post(self, request, *args, **kwargs):
        result = u''
        try:
            amount_str = request.POST.get('amount', '')
            amount = decimal.Decimal(amount_str). \
                quantize(TWO_PLACES, context=decimal.Context(traps=[decimal.Inexact]))
            amount_str = str(amount)

            card_id = request.POST.get('card_id', '')
            card = Card.objects.get(pk=card_id)

            pay_info = PayInfo()
            pay_info.amount = amount_str
            pay_info.type = PayInfo.WITHDRAW
            pay_info.user = request.user
            pay_info.status = PayInfo.INITIAL
            pay_info.save()

            post = dict()
            post['OrdId'] = str(pay_info.pk)
            post['OrdAmt'] = amount_str
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
        except (socket.error, SignException) as e:
            result = u'系统内部错误,请重试'
            pay_info.error_message = str(e)
            pay_info.status = PayInfo.FAIL
            pay_info.save()
            logger.fatal('sign error! order id: ' + str(pay_info.pk) + ' ' + str(e))

        if result:
            return self.render_to_response({
                'result': result
            })

        user_margin = UserMarginManager(request.user)
        user_margin.freeze(amount)
        try:
            r = requests.post(form['url'], form['post'])
            root = ET.fromstring(r.text.encode('utf-8'))
            ret = root.find('result')
            data = dict()
            for child in ret:
                data[child.tag] = child.text
        except requests.exceptions.ConnectionError as e:
            result = u'系统内部错误,请重试'
            pay_info.status = PayInfo.FAIL
            pay_info.error_message = str(e)
            pay_info.save()
            logger.error('connection error. order id: %s. exception: %s', str(pay_info.pk), str(e))
            user_margin.unfreeze(amount)
        except (requests.exceptions.HTTPError, requests.exceptions.Timeout, ET.ParseError) as e:
            result = u'系统内部错误,请联系客服人员'
            pay_info.status = PayInfo.EXCEPTION
            pay_info.error_message = str(e)
            pay_info.save()
            logger.fatal('unexpected error. order id: %s. exception: %s', str(pay_info.pk), str(e))

        if result:
            return self.render_to_response({
                'result': result
            })

        result = handle_withdraw_result(data, request.user)
        return self.render_to_response({
            'result': result
        })


class WithdrawCallback(View):
    def post(self, request, *args, **kwargs):
        handle_withdraw_result(request.POST.dict())
        order_id = request.POST.get('OrdId', '')
        return HttpResponse('RECV_ORD_ID_' + order_id)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(WithdrawCallback, self).dispatch(request, *args, **kwargs)

