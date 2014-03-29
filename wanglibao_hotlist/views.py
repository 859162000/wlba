from django.shortcuts import render
from rest_framework import viewsets
from wanglibao_account.permissions import IsAdminUserOrReadOnly
from wanglibao_hotlist.models import HotTrust, HotFinancing, HotFund
from wanglibao_hotlist.serializers import HotFundSerializer


class HotTrustViewSet(viewsets.ModelViewSet):
    model = HotTrust
    permission_classes = (IsAdminUserOrReadOnly,)


class HotFinancingViewSet(viewsets.ModelViewSet):
    model = HotFinancing
    permission_classes = (IsAdminUserOrReadOnly,)


class HotFundViewSet(viewsets.ModelViewSet):
    model = HotFund
    serializer_class = HotFundSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
