# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View
from rest_framework.response import Response
from rest_framework.views import APIView
from wanglibao_buy.models import Bank
from wanglibao_pay.huifu_pay import HuifuPay
from wanglibao_pay.models import PayInfo
import requests
import xml.etree.ElementTree as ET


class BankListView(TemplateView):
    template_name = 'pay_banks.jade'

    def get_context_data(self, **kwargs):
        return dict(banks=Bank.objects.all())


class Pay(APIView):
    permission_classes = ()
    def post(self, request):
        amount = request.DATA.get('amount', '')
        gate_id = request.DATA.get('gate_id', '')
        pay_info = PayInfo()
        pay_info.amount = float(amount)
        pay_info.type = 'D'
        pay_info.user = request.user
        pay_info.save()
        post = {
            'OrdId': pay_info.pk,
            'GateId': gate_id,
            'OrdAmt': amount
        }
        pay = HuifuPay()
        form = pay.pay(post)

        return Response({
            'form': form
        })


class WithdrawCompleteView(TemplateView):
    template_name = 'withdraw_complete.jade'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
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
        pay = HuifuPay()
        for child in result:
            data[child.tag] = child.text
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
            print 'order ID:', order_id
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

