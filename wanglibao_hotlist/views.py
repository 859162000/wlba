from django.shortcuts import render
from rest_framework import viewsets
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao_account.permissions import IsAdminUserOrReadOnly
from wanglibao_hotlist.models import HotTrust, HotFinancing, HotFund, MobileHotFund, MobileHotTrust
from wanglibao_hotlist.serializers import HotFundSerializer, MobileHotFundSerializer, MobileHotTrustSerializer


class HotTrustViewSet(viewsets.ModelViewSet):
    model = HotTrust
    permission_classes = IsAdminUserOrReadOnly,


class HotFinancingViewSet(viewsets.ModelViewSet):
    model = HotFinancing
    permission_classes = IsAdminUserOrReadOnly,


class HotFundViewSet(viewsets.ModelViewSet):
    model = HotFund
    serializer_class = HotFundSerializer
    permission_classes = IsAdminUserOrReadOnly,


class MobileHotFundViewSet(PaginatedModelViewSet):
    model = MobileHotFund
    serializer_class = MobileHotFundSerializer
    permission_classes = IsAdminUserOrReadOnly,


class MobileHotTrustViewSet(PaginatedModelViewSet):
    model = MobileHotTrust
    serializer_class = MobileHotTrustSerializer
    permission_classes = IsAdminUserOrReadOnly,