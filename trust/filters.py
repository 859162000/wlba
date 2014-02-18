import django_filters
from rest_framework.filters import FilterSet
from trust.models import Trust


class TrustFilterSet(FilterSet):
    min_rate = django_filters.NumberFilter(name="expected_earning_rate", lookup_type='gte')
    max_rate = django_filters.NumberFilter(name="expected_earning_rate", lookup_type='lt')
    min_scale = django_filters.NumberFilter(name="scale", lookup_type='gte')
    max_scale = django_filters.NumberFilter(name="scale", lookup_type='lt')
    min_period = django_filters.NumberFilter(name="period", lookup_type='gte')
    max_period = django_filters.NumberFilter(name="period", lookup_type='lt')
    min_threshold = django_filters.NumberFilter(name="investment_threshold", lookup_type='gte')
    max_threshold = django_filters.NumberFilter(name="investment_threshold", lookup_type='lt')

    class Meta:
        model = Trust
        fields = ['name',
                  'short_name',
                  'expected_earning_rate',
                  'issuer__name',
                  'available_region',
                  'investment_threshold',
                  'min_rate', 'max_rate',
                  'min_scale', 'max_scale',
                  'min_period', 'max_period',
                  ]
