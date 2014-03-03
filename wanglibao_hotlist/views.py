from django.shortcuts import render
from rest_framework import viewsets
from wanglibao_hotlist.models import HotTrust, HotFinancing, HotFund
from wanglibao_hotlist.serializers import HotFundSerializer


class HotTrustViewSet(viewsets.ModelViewSet):
    model = HotTrust


class HotFinancingViewSet(viewsets.ModelViewSet):
    model = HotFinancing


class HotFundViewSet(viewsets.ModelViewSet):
    model = HotFund
    serializer_class = HotFundSerializer
