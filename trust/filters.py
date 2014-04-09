import django_filters
from trust.models import Trust
from wanglibao.filters import AutoNumberFilter


class TrustFilterSet(AutoNumberFilter):
    issuer_name = django_filters.CharFilter(name="issuer__short_name")

    class Meta(AutoNumberFilter.Meta):
        model = Trust
        number_fields = (
            ('threshold', 'investment_threshold'),
            ('period', 'period'),
            ('rate', 'expected_earning_rate'),
            ('scale', 'scale')
        )