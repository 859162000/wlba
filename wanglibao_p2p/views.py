# encoding: utf8
from django.contrib.admin.views.decorators import staff_member_required

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from marketing.models import SiteData
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao_p2p.forms import PurchaseForm
from wanglibao_p2p.keeper import ProductKeeper
from wanglibao_p2p.models import P2PProduct
from wanglibao_p2p.serializers import P2PProductSerializer, P2PRecordSerializer
from wanglibao_p2p.trade import P2PTrader
from wanglibao.const import ErrorNumber


class P2PDetailView(TemplateView):
    template_name = "p2p_detail.jade"

    def get_context_data(self, id, **kwargs):
        status = 'finished'

        try:
            p2p = P2PProduct.objects.get(pk=id)
            form = PurchaseForm(initial={'product': p2p})

            if p2p.soldout_time:
                end_time = p2p.soldout_time
            else:
                end_time = p2p.end_time

            if p2p.status != u'正在招标':
                status = 'finished'
            else:
                if p2p.publish_time <= timezone.now() < p2p.end_time:
                    status = 'open'
                elif timezone.now() > p2p.end_time:
                    status = 'finished'

        except P2PProduct.DoesNotExist:
            raise Http404(u'您查找的产品不存在')

        user = self.request.user
        current_equity = 0

        if user.is_authenticated():
            equity_record = p2p.equities.filter(user=user).first()
            if equity_record is not None:
                current_equity = equity_record.equity

        orderable_amount = min(p2p.limit_amount_per_user - current_equity, p2p.remain)

        site_data = SiteData.objects.all()[0]

        return {
            'p2p': p2p,
            'form': form,
            'status': status,
            'end_time': end_time,
            'orderable_amount': orderable_amount,
            'current_equity': current_equity,
            'site_data': site_data
        }


class PurchaseP2P(APIView):
    permission_classes = ()

    @property
    def allowed_methods(self):
        return ['POST']

    def post(self, request):
        if not request.user.is_authenticated():
            return Response({
                'message': u'请登录',
                'error_number': ErrorNumber.unauthorized
            }, status=status.HTTP_403_FORBIDDEN)
        if not request.user.wanglibaouserprofile.id_is_valid:
            return Response({
                'message': u'请先进行实名认证',
                'error_number': ErrorNumber.need_authentication
            }, status=status.HTTP_400_BAD_REQUEST)
        form = PurchaseForm(request.DATA)
        if form.is_valid():
            p2p = form.cleaned_data['product']
            amount = form.cleaned_data['amount']

            try:
                trader = P2PTrader(product=p2p, user=request.user)
                product_info, margin_info, equity_info = trader.purchase(amount)
                return Response({
                    'data': product_info.amount
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


class AuditProductView(TemplateView):
    template_name = 'audit_p2p.jade'

    def get_context_data(self, **kwargs):
        pk = kwargs['id']
        p2p = P2PProduct.objects.get(pk=pk)

        if p2p.status != u'满标待审核':
            return HttpResponse(u'产品状态不是满标待审核')

        return {
            "p2p": p2p
        }

    def post(self, request, **kwargs):
        pk = kwargs['id']
        p2p = P2PProduct.objects.get(pk=pk)
        ProductKeeper(p2p).audit(request.user)
        return HttpResponseRedirect('/admin/wanglibao_p2p/p2pproduct/')


audit_product_view = staff_member_required(AuditProductView.as_view())


class P2PProductViewSet(PaginatedModelViewSet):
    model = P2PProduct
    permission_classes = IsAdminUserOrReadOnly,
    serializer_class = P2PProductSerializer


class RecordView(APIView):
    permission_classes = ()

    def get(self, request, product_id):
        try:
            product = P2PProduct.objects.get(pk=product_id)
        except P2PProduct.DoesNotExist:
            return Response(
                status=404
            )

        equities = product.p2precord_set.filter(catalog=u'申购').prefetch_related('user').prefetch_related('user__wanglibaouserprofile')

        serializer = P2PRecordSerializer(equities, many=True, context={"request": request})

        return Response(data=serializer.data)