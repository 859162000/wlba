import django_filters
from wanglibao.filters import AutoNumberFilter
from wanglibao_fund.models import Fund


class FundFilterSet(AutoNumberFilter):
    class Meta(AutoNumberFilter.Meta):
        model = Fund
        number_fields = (
            ('rate_today', 'rate_today'),
            ('earned_per_10k', 'earned_per_10k'),
            ('rate_7_days', 'rate_7_days'),
            ('rate_1_month', 'rate_1_month'),
            ('rate_3_months', 'rate_3_months'),
            ('rate_6_months', 'rate_6_months'),
            ('rate_1_year', 'rate_1_year'),
        )
