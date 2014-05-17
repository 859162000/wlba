from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer
from models import Issuer, Trust


class IssuerSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Issuer


class TrustSerializer(HyperlinkedModelSerializer):
    """
    The trust serializer for wanglibao. It adds the issuer name to the object's output
    """
    class Meta:
        model = Trust
        depth = 1

    issuer_short_name = serializers.SerializerMethodField('get_issuer_short_name')
    issuer_description = serializers.SerializerMethodField('get_issuer_description')
    id = serializers.IntegerField('id')

    @staticmethod
    def get_issuer_short_name(trust):
        return trust.issuer.short_name

    @staticmethod
    def get_issuer_description(trust):
        return trust.issuer.note
