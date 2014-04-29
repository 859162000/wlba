import django_filters
from rest_framework import filters


class OrderingFilter(filters.OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        qs = super(OrderingFilter, self).filter_queryset(request, queryset, view)

        count = request.QUERY_PARAMS.get('count', None)
        if count is not None:
            qs = qs[0:count]

        return qs

    def remove_invalid_fields(self, queryset, ordering, view):
        """
        Overwrite the default behavior
        Prevent remove field names in format related__sub_field
        """
        field_names = [field.name for field in queryset.model._meta.fields]
        field_names += queryset.query.aggregates.keys()
        return [term for term in ordering if term.lstrip('-') in field_names or term.find('__') >= 0]


class AutoNumberFilter(filters.FilterSet):

    class Meta:
        number_lookup_types = ('gt', 'gte', 'lt', 'lte', ('max', 'lt'), ('min', 'gte'))
        number_fields = []

    def __init__(self, *args, **kwargs):
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

        super(AutoNumberFilter, self).__init__(*args, **kwargs)
