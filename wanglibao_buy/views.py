from django.db.models import F, Sum
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from trust.models import Trust
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao_buy.models import TradeInfo, DailyIncome
from wanglibao_buy.serializers import TradeInfoSerializer, DailyIncomeSerializer
from wanglibao_fund.models import Fund


def get_product_qs(type):
    if type == 'fund':
        return Fund.objects.all()
    if type == 'trust':
        return Trust.objects.all()

    raise NotImplementedError('The type not supported yet')


def update_and_save_product_trade_info(trade_info):
    item_type = trade_info.type
    item_id = trade_info.item_id
    amount = trade_info.amount
    user = trade_info.user

    already_bought = TradeInfo.objects.filter(type=item_type, item_id=item_id, user=user).exists()

    # Now find the product and update the buy info
    product = get_product_qs(item_type).filter(pk=item_id).first()
    product.bought_count = F('bought_count') + 1
    if not already_bought:
        product.bought_people_count = F('bought_people_count') + 1
    product.bought_amount = F('bought_amount') + amount

    trade_info.save()
    product.save()


class TradeInfoViewSet(PaginatedModelViewSet):
    model = TradeInfo
    serializer_class = TradeInfoSerializer
    permission_classes = IsAuthenticated,

    def create(self, request, *args, **kwargs):
        data = request.DATA.copy()
        type = data.get('type')
        if type == 'fund':
            fund_code = data.get('fund_code')
            if fund_code is not None:
                data['item_id'] = Fund.objects.filter(product_code=fund_code).first().id

        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            user = None
            if request.user and request.user.is_authenticated():
                user = request.user

            serializer.object.user = user
            update_and_save_product_trade_info(serializer.object)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': serializer.errors
            }, status=400)

    def get_queryset(self):
        user = self.request.user
        return TradeInfo.objects.filter(user=user)


class DailyIncomeViewSet(ReadOnlyModelViewSet):
    model = DailyIncome
    permission_classes = IsAuthenticated,
    serializer_class = DailyIncomeSerializer

    def get_queryset(self):
        user = self.request.user
        return DailyIncome.objects.filter(user=user)


class TotalIncome(APIView):
    permission_classes = IsAuthenticated,

    def get(self, request, *args, **kwargs):

        user = request.user
        total_income = DailyIncome.objects.filter(user=user).aggregate(Sum('income'))
        return Response({
            'total_income': total_income['income__sum']
        })