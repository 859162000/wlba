from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View
from rest_framework.response import Response
from rest_framework.views import APIView
from wanglibao_buy.models import Bank
from wanglibao_pay.huifu_pay import HuifuPay
from wanglibao_pay.models import PayInfo


class BankListView(TemplateView):
    template_name = 'pay_banks.jade'

    def get_context_data(self, **kwargs):
        return {
            'banks': Bank.objects.all(),
        }


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


class PayCallback(View):
    def post(self, request, *args, **kwargs):
        pay = HuifuPay()
        if pay.verify_sign(request.POST.dict()):
            order_id = request.POST.get('OrdId', '')
            return HttpResponse('RECV_ORD_ID_' + order_id)
        else:
            return HttpResponseBadRequest()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(PayCallback, self).dispatch(request, *args, **kwargs)

