import django_filters
from rest_framework.filters import FilterSet
from wanglibao_portfolio.models import Portfolio


class PortfolioFilterSet(FilterSet):
    name = django_filters.CharFilter(name="name")
    asset_min = django_filters.NumberFilter(name="asset_min", lookup_type="lte")
    asset_max = django_filters.NumberFilter(name="asset_max", lookup_type="gt")
    period_min = django_filters.NumberFilter(name="period_min", lookup_type="lte")
    period_max = django_filters.NumberFilter(name="period_max", lookup_type="gt")

    class Meta:
        model = Portfolio
