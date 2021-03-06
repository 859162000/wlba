# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao_fund.models import Fund
from wanglibao_hotlist.models import HotTrust, HotFinancing, HotFund, MobileHotFund, MobileHotTrust, MobileMainPage, \
    MobileMainPageP2P
from wanglibao_hotlist.serializers import HotFundSerializer, MobileHotFundSerializer, MobileHotTrustSerializer, \
    MobileMainPageSerializer, MobileMainPageP2PSerializer
from wanglibao_p2p.models import P2PProduct


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


class MobileMainPageP2PViewSet(PaginatedModelViewSet):
    model = MobileMainPageP2P
    serializer_class = MobileMainPageP2PSerializer

    def get_queryset(self):

        h = MobileMainPageP2P()
        if self.model.objects.all().exists():

            mp = MobileMainPageP2P.objects.filter(item__status=u'正在招标', item__hide=False).order_by('-hot_score').first()
            if mp:
                return [mp]
            else:
                item = P2PProduct.objects.filter(hide=False, end_time__gt=timezone.now()).\
                    filter(status=u'正在招标').order_by('-priority').first()
                if not item:
                    item = P2PProduct.objects.filter(hide=False, end_time__gt=timezone.now()).filter(status__in=[
                        u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中'])\
                    .order_by('-soldout_time').first()

        else:
            item = P2PProduct.objects.filter(hide=False, end_time__gt=timezone.now()).\
                    filter(status=u'正在招标').order_by('-priority').first()
            if not item:
                item = P2PProduct.objects.filter(hide=False, end_time__gt=timezone.now()).filter(status__in=[
                    u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中'])\
                .order_by('-soldout_time').first()

        h.item = item
        h.added = timezone.now()
        h.hot_score = 1
        return [h]

        # return super(MobileMainPageP2PViewSet, self).get_queryset()