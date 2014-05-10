# encoding:utf8
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao_banner.filter import BannerFilterSet
from wanglibao_banner.models import Banner
from wanglibao_banner.serializer import BannerSerializer


class BannerViewSet(PaginatedModelViewSet):
    """
    广告条
    """
    model = Banner
    serializer_class = BannerSerializer
    filter_class = BannerFilterSet
    permission_classes = (IsAdminUserOrReadOnly,)
