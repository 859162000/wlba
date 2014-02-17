from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer
from wanglibao_bank_financing.models import BankFinancing


class BankFinancingSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = BankFinancing

    bank_name = serializers.SerializerMethodField('get_bank_name')

    @classmethod
    def get_bank_name(cls, bank_financing):
        return bank_financing.bank.name