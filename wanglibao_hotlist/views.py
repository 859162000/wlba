from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao_fund.models import Fund
from wanglibao_hotlist.models import HotTrust, HotFinancing, HotFund, MobileHotFund, MobileHotTrust, MobileMainPage
from wanglibao_hotlist.serializers import HotFundSerializer, MobileHotFundSerializer, MobileHotTrustSerializer, \
    MobileMainPageSerializer


class HotViewSetBase(viewsets.ModelViewSet):
    permission_classes = IsAdminUserOrReadOnly,

class HotTrustViewSet(viewsets.ModelViewSet):
    model = HotTrust


class HotFinancingViewSet(viewsets.ModelViewSet):
    model = HotFinancing


class HotFundViewSet(viewsets.ModelViewSet):
    model = HotFund
    serializer_class = HotFundSerializer


class MobileHotFundViewSet(PaginatedModelViewSet):
    model = MobileHotFund
    serializer_class = MobileHotFundSerializer


class MobileHotTrustViewSet(PaginatedModelViewSet):
    model = MobileHotTrust
    serializer_class = MobileHotTrustSerializer


class MobileMainPageViewSet(PaginatedModelViewSet):
    model = MobileMainPage
    serializer_class = MobileMainPageSerializer

    def get_queryset(self):
        if not self.model.objects.all().exists():
            h = MobileMainPage()
            h.item = Fund.objects.filter(availablefund__isnull=False).order_by('-rate_7_days').first()
            h.added = timezone.now()
            h.hot_score = 1

            return [h]

        return super(MobileMainPageViewSet, self).get_queryset()
