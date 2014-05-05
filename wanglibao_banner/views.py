from django.shortcuts import render

from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao_banner.filter import BannerFilterSet
from wanglibao_banner.models import Banner
from wanglibao_banner.serializer import BannerSerializer


class BannerViewSet(PaginatedModelViewSet):
    model = Banner
    serializer_class = BannerSerializer
    filter_class = BannerFilterSet
    queryset = Banner.objects.all().order_by('-priority', '-last_updated')
