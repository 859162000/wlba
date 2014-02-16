import django_filters
from rest_framework.filters import FilterSet
from wanglibao_bank_financing.models import BankFinancing


class BankFinancingFilterSet(FilterSet):
    name = django_filters.CharFilter(name="name")
    min_rate = django_filters.NumberFilter(name="max_expected_profit_rate", lookup_type='gte')
    max_rate = django_filters.NumberFilter(name="max_expected_profit_rate", lookup_type='lt')
    min_period = django_filters.NumberFilter(name="period", lookup_type='gte')
    max_period = django_filters.NumberFilter(name="period", lookup_type='lt')
    min_threshold = django_filters.NumberFilter(name="invest_threshold", lookup_type='gte')
    max_threshold = django_filters.NumberFilter(name="invest_threshold", lookup_type='lt')
    bank = django_filters.CharFilter(name="bank__name", )
    currency = django_filters.CharFilter(name="currency")
    profit_type = django_filters.CharFilter(name="profit_type")
    product_type = django_filters.CharFilter(name="product_type")
    principle_guaranteed = django_filters.BooleanFilter(name="principle_guaranteed")
    product_code = django_filters.CharFilter(name="product_code")

    class Meta:
        model = BankFinancing
        fields = ['name',
                  'max_expected_profit_rate',
                  'bank',
                  'currency',
                  'profit_type',
                  'product_type',
                  'principle_guaranteed',
                  'product_code',
                  'min_rate', 'max_rate',
                  'min_period', 'max_period',
                  'min_threshold', 'max_threshold'
                  ]