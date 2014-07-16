# coding=utf-8
from django.http import HttpResponse
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao.permissions import AllowAnyPostOnlyAdminList
from wanglibao_preorder.forms import PreOrderP2PForm

from wanglibao_preorder.models import PreOrder
from wanglibao_preorder.serializers import PreOrderSerializer


class PreOrderViewSet(PaginatedModelViewSet):
    model = PreOrder
    serializer = PreOrderSerializer
    throttle_classes = (UserRateThrottle,)
    permission_classes = AllowAnyPostOnlyAdminList,

    @property
    def allowed_methods(self):
        return 'POST', 'GET'

    def create(self, request):
        serializer = self.serializer(data=request.DATA)

        if serializer.is_valid():
            user = None
            if request.user and request.user.is_authenticated():
                user = request.user

            serializer.object.user = user
            serializer.object.save()
            return Response(serializer.data)
        else:
            return Response({
                'message': 'failed'
            }, status=400)


class PreOrderP2PView(TemplateView):

    template_name = 'preorder_p2p.html'

    def post(self, request):
        form = PreOrderP2PForm(data=request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            phone = form.cleaned_data.get('phone')
            amount = form.cleaned_data.get('amount')
            preorder = PreOrder(user_name=name, phone=phone, amount=amount, product_type='p2p')
            preorder.save()
            return HttpResponse(u'您的预约请求已经收到')
        else:
            return HttpResponse(u'您的预约请求数据格式不对')
