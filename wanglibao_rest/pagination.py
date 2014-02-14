from rest_framework import serializers
from rest_framework.pagination import PaginationSerializer as RestPaginationSerializer


class PaginationSerializer(RestPaginationSerializer):
    num_pages = serializers.Field(source='paginator.num_pages')
