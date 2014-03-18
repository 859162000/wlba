from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer
from wanglibao_bank_financing.models import BankFinancing, Bank


class BankFinancingSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = BankFinancing

    bank_name = serializers.SerializerMethodField('get_bank_name')
    id = serializers.IntegerField('id')

    @classmethod
    def get_bank_name(cls, bank_financing):
        return bank_financing.bank.name


class BankSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Bank

    logo = serializers.SerializerMethodField('logo_url')
    id = serializers.IntegerField('id')

    @classmethod
    def logo_url(cls, bank):
        if bank.logo:
            return bank.logo.url
        else:
            return ""

