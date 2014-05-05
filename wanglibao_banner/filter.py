from rest_framework.filters import FilterSet
from wanglibao_banner.models import Banner


class BannerFilterSet(FilterSet):
    class Meta:
        model = Banner