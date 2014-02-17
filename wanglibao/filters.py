from rest_framework import filters


class OrderingFilter(filters.OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        qs = super(OrderingFilter, self).filter_queryset(request, queryset, view)

        count = request.QUERY_PARAMS.get('count', None)
        if count is not None:
            qs = qs[0:count]

        return qs
