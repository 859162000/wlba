import django_filters
from django_filters.filterset import get_declared_filters
from rest_framework.filters import FilterSet
from trust.models import Trust
from wanglibao.filters import AutoNumberFilter


class TrustFilterSet(AutoNumberFilter):
    class Meta(AutoNumberFilter.Meta):
        model = Trust
        number_fields = (
            ('threshold', 'investment_threshold'),
            ('period', 'period'),
            ('rate', 'expected_earning_rate'),
            ('scale', 'scale')
        )