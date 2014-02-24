import django_filters
from wanglibao.filters import AutoNumberFilter
from wanglibao_bank_financing.models import BankFinancing


class BankFinancingFilterSet(AutoNumberFilter):

    bank_name = django_filters.CharFilter(name="bank__name")

    class Meta(AutoNumberFilter.Meta):
        model = BankFinancing
        number_fields = (
            ('threshold', 'invest_threshold'),
            ('period', 'period'),
            ('rate', 'max_expected_profit_rate'),
        )
