import django_filters
from django_filters.filterset import get_declared_filters
from rest_framework.filters import FilterSet
from trust.models import Trust


class TrustFilterSet(FilterSet):
    class Meta:
        model = Trust
        number_fields = (
            ('threshold', 'investment_threshold'),
            ('period', 'period'),
            ('rate', 'expected_earning_rate'),
            ('scale', 'scale')
        )
        number_lookup_types = ('gt', 'gte', 'lt', 'lte', ('max', 'lt'), ('min', 'gte'))

    def __init__(self, *args, **kwargs):
        super(TrustFilterSet, self).__init__(*args, **kwargs)

        number_fields = self.Meta.number_fields
        number_lookup_types = self.Meta.number_lookup_types
        attrs = {}

        for field, source_field in number_fields:
            attrs[field] = django_filters.NumberFilter(name=source_field)

            for lookup_type in number_lookup_types:
                if isinstance(lookup_type, tuple):
                    name, operator = lookup_type
                    attrs[name + '_' + field] = django_filters.NumberFilter(name=source_field, lookup_type=operator)
                else:
                    attrs[str(lookup_type) + '_' + field] = django_filters.NumberFilter(name=source_field, lookup_type=lookup_type)

        for name, filter in attrs.items():
            self.base_filters[name] = filter
