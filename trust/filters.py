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