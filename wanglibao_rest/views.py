from django.contrib.auth.models import User, Group, Permission

# Create your views here.
from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets
from trust.models import Trust, Issuer
from wanglibao_rest.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    model = User
    serializer_class = UserSerializer


class TrustViewSet(viewsets.ModelViewSet):
    model = Trust
    filter_fields = ('name', 'short_name', 'expected_earning_rate')


class IssuerViewSet(viewsets.ModelViewSet):
    model = Issuer


