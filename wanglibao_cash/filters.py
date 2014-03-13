import django_filters
from wanglibao.filters import AutoNumberFilter
from wanglibao_cash.models import Cash


class CashFilterSet(AutoNumberFilter):
    issuer_name = django_filters.CharFilter(name="issuer__name", )

    class Meta(AutoNumberFilter.Meta):
        model = Cash
        number_fields = [
            ('period', 'period'),
            ('profit_rate_7days', 'profit_rate_7days'),
                 ]