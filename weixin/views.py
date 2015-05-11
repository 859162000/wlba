# encoding:utf-8
from django.views.generic import View, TemplateView
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Account
from wechatpy import parse_message, create_reply
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from .common.wechat import tuling
from wanglibao_p2p.models import P2PProduct
from wanglibao_p2p.amortization_plan import get_amortization_plan
from django.db.models import Q
import datetime
from decimal import Decimal
# Create your views here.


class ConnectView(View):

    def check_signature(self, request, id):
        try:
            account = Account.objects.get(pk=id)
        except Account.DoesNotExist:
            return False

        try:
            check_signature(
                account.token,
                request.GET.get('signature'),
                request.GET.get('timestamp'),
                request.GET.get('nonce')
            )
        except InvalidSignatureException:
            return False

        return True

    def get(self, request, id):
        if not self.check_signature(request, id):
            return HttpResponseForbidden()

        return HttpResponse(request.GET.get('echostr'))

    def post(self, request, id):
        if not self.check_signature(request, id):
            return HttpResponseForbidden()

        msg = parse_message(request.body)

        if msg.type == 'text':

            reply = tuling(msg)
        else:
            reply = create_reply(u'更多功能，敬请期待！', msg)

        return HttpResponse(reply.render())

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ConnectView, self).dispatch(request, *args, **kwargs)


class P2PListView(TemplateView):
    template_name = 'weixin_list.jade'

    def get_context_data(self, **kwargs):
        p2p_lists = P2PProduct.objects.filter(hide=False).filter(status__in=[
            u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标'
        ]).exclude(Q(category=u'票据') | Q(category=u'酒仙众筹标')).order_by('-priority', '-publish_time')[:10]

        return {
            'p2p_lists': p2p_lists
        }


class P2PDetailView(TemplateView):
    template_name = "weixin_detail.jade"

    def get_context_data(self, id, **kwargs):
        context = super(P2PDetailView, self).get_context_data(**kwargs)

        try:
            p2p = P2PProduct.objects.select_related('activity').exclude(status=u'流标').exclude(status=u'录标')\
                .get(pk=id, hide=False)

            if p2p.soldout_time:
                end_time = p2p.soldout_time
            else:
                end_time = p2p.end_time
        except P2PProduct.DoesNotExist:
            raise Http404(u'您查找的产品不存在')

        terms = get_amortization_plan(p2p.pay_method).generate(p2p.total_amount,
                                                               p2p.expected_earning_rate / 100,
                                                               datetime.datetime.now(),
                                                               p2p.period)
        total_earning = terms.get("total") - p2p.total_amount
        total_fee_earning = 0

        if p2p.activity:
            total_fee_earning = Decimal(p2p.total_amount * p2p.activity.rule.rule_amount *
                                        (Decimal(p2p.period) / Decimal(12))).quantize(Decimal('0.01'))

        current_equity = 0

        orderable_amount = min(p2p.limit_amount_per_user - current_equity, p2p.remain)

        context.update({
            'p2p': p2p,
            'end_time': end_time,
            'orderable_amount': orderable_amount,
            'total_earning': total_earning,
            'current_equity': current_equity,
            'attachments': p2p.attachment_set.all(),
            'total_fee_earning': total_fee_earning,
        })

        return context


