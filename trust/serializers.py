from django.contrib.auth.models import User
from rest_framework.serializers import HyperlinkedModelSerializer
from models import Issuer


class UserSerializer (HyperlinkedModelSerializer):
    """
    The user serializer for wanglibao user resource
    """
    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'first_name', 'last_name', 'email', 'date_joined')


class IssuerSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Issuer

