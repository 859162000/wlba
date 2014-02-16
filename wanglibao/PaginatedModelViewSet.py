from rest_framework.viewsets import ModelViewSet


class PaginatedModelViewSet(ModelViewSet):
    paginate_by = 20
    paginate_by_param = 'page_size'
    max_paginate_by = 100
