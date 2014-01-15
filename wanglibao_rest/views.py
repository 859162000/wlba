from django.contrib.auth.models import User, Group, Permission

# Create your views here.
from django.contrib.contenttypes.models import ContentType
import django_filters
from rest_framework import viewsets
from rest_framework.filters import FilterSet
from trust.models import Trust, Issuer
from wanglibao_rest.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    model = User
    serializer_class = UserSerializer


class TrustFilterSet(FilterSet):
    min_rate = django_filters.NumberFilter(name="expected_earning_rate", lookup_type='gte')
    max_rate = django_filters.NumberFilter(name="expected_earning_rate", lookup_type='lte')
    min_scale = django_filters.NumberFilter(name="scale", lookup_type='gte')
    max_scale = django_filters.NumberFilter(name="scale", lookup_type='lte')

    class Meta:
        model = Trust
        fields = ['name',
                  'short_name',
                  'expected_earning_rate',
                  'issuer__name',
                  'available_region',
                  'investment_threshold',
                  'min_rate', 'max_rate',
                  'min_scale', 'max_scale',
                  ]


class TrustViewSet(viewsets.ModelViewSet):
    model = Trust
    filter_class = TrustFilterSet


class IssuerViewSet(viewsets.ModelViewSet):
    model = Issuer


