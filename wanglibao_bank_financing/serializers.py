from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer
from wanglibao_bank_financing.models import BankFinancing, Bank


class BankFinancingSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = BankFinancing

    bank_name = serializers.SerializerMethodField('get_bank_name')

    @classmethod
    def get_bank_name(cls, bank_financing):
        return bank_financing.bank.name


class BankSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Bank

    logo = serializers.SerializerMethodField('logo_url')

    def logo_url(self, bank):
        return bank.logo.url

