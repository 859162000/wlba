# -*- coding: utf-8 -*-
import logging
import socket
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View
from wanglibao_buy.models import Bank
from wanglibao_pay.huifu_pay import HuifuPay, SignException
from wanglibao_pay.models import PayInfo
import requests
import xml.etree.ElementTree as ET
import decimal

logger = logging.getLogger(__name__)

class BankListView(TemplateView):
    template_name = 'pay_banks.jade'

    def get_context_data(self, **kwargs):
        return {
            'banks': Bank.objects.all(),
        }


class PayView(TemplateView):
    template_name = ''
    TWO_PLACES = decimal.Decimal(10) ** -2

    def post(self, request):
        try:
            amount_str = request.DATA.get('amount', '')
            amount = decimal.Decimal(amount_str).\
                quantize(PayView.TWO_PLACES, context=decimal.Context(traps=[decimal.Inexact]))
            amount_str = str(amount)
            #todo: validate gate id
            gate_id = request.DATA.get('gate_id', '')

            pay_info = PayInfo()
            pay_info.amount = amount
            pay_info.type = 'P'
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
            pay_info.status = PayInfo.PROCESSING
            pay_info.save()
        except decimal.DecimalException:
            message = u'金额格式错误'
        except (socket.error, SignException) as e:
            message = u'系统内部错误,请重试'
            pay_info.status = PayInfo.FAIL
            pay_info.error_message = e.message
            pay_info.save()
            logger.fatal('sign error! order id: ' + str(pay_info.pk) + ' ' + e.message)

        context = {
            'message': message,
            'form': form
        }
        return self.render_to_response(context)


class WithdrawCompleteView(TemplateView):
    template_name = 'withdraw_complete.jade'

    def post(self, request, *args, **kwargs):
        amount = request.POST.get('amount', '')
        pay_info = PayInfo()
        pay_info.amount = float(amount)
        pay_info.type = 'W'
        pay_info.user = request.user
        pay_info.save()

        post = dict()
        post['OrdId'] = str(pay_info.pk)
        post['OrdAmt'] = '500.00'
        post['AcctName'] = u'用户'
        post['BankId'] = 'CCB'
        post['AcctId'] = '62225888'
        post['PrPurpose'] = 'p2p'

        pay = HuifuPay()
        form = pay.withdraw(post)

        r = requests.post(form['url'], form['post'])
        root = ET.fromstring(r.text.encode('utf-8'))
        result = root.find('result')
        data = dict()
        for child in result:
            data[child.tag] = child.text
        context = dict()
        pay = HuifuPay()
        if pay.verify_sign(data, HuifuPay.WITHDRAW_FIELDS) and data['RespCode'] == '000':
            context['result'] = u'提款成功'
        else:
            context['result'] = u'提款失败'
        return self.render_to_response(context)


class PayCallback(View):
    def post(self, request, *args, **kwargs):
        pay = HuifuPay()
        if pay.verify_sign(request.POST.dict(), HuifuPay.PAY_FIELDS):
            order_id = request.POST.get('OrdId', '')
            pay_info = PayInfo.objects.get(pk=order_id)
            print str(request.POST.dict())
            pay_info.status = PayInfo.SUCCESS
            pay_info.save()
            return HttpResponse('RECV_ORD_ID_' + order_id)
        else:
            return HttpResponseBadRequest()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(PayCallback, self).dispatch(request, *args, **kwargs)


class WithdrawCallback(View):
    def post(self, request, *args, **kwargs):
        pay = HuifuPay()
        if pay.verify_sign(request.POST.dict(), HuifuPay.WITHDRAW_FIELDS):
            order_id = request.POST.get('OrdId', '')
            return HttpResponse('RECV_ORD_ID_' + order_id)
        else:
            return HttpResponseBadRequest()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(WithdrawCallback, self).dispatch(request, *args, **kwargs)

