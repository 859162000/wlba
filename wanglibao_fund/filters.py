import django_filters
from rest_framework.filters import FilterSet
from wanglibao_fund.models import Fund


class FundFilterSet(FilterSet):
    name = django_filters.CharFilter(name="name")
    type = django_filters.CharFilter(name="type")
    status = django_filters.CharFilter(name="status")
    issuer_name = django_filters.CharFilter(name="issuer__name", )
    product_code = django_filters.CharFilter(name="product_code")

    class Meta:
        model = Fund
        fields = ['name',
                  'type',
                  'status',
                  'issuer_name',
                  'product_code',
                 ]