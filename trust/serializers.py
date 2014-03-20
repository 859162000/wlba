from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer
from models import Issuer, Trust


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


class TrustSerializer(HyperlinkedModelSerializer):
    """
    The trust serializer for wanglibao. It adds the issuer name to the object's output
    """
    class Meta:
        model = Trust

    issuer_short_name = serializers.SerializerMethodField('get_issuer_short_name')
    id = serializers.IntegerField('id')

    def get_issuer_short_name(self, trust):
        return trust.issuer.short_name