from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer
from wanglibao_cash.models import Cash, CashIssuer


class CashSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Cash

    issuer_name = serializers.SerializerMethodField('get_issuer_name')

    @classmethod
    def get_issuer_name(cls, cash):
        return cash.issuer.name


class CashIssuerSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = CashIssuer

    logo = serializers.SerializerMethodField('logo_url')

    @classmethod
    def logo_url(cls, cash_issuer):
        if cash_issuer.logo:
            return cash_issuer.logo.url
        else:
            return ""