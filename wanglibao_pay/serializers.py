from rest_framework import serializers
from wanglibao_pay.models import Card, Bank

class BankSerializer(serializers.ModelSerializer):
    bank_limit = serializers.Field()
    class Meta:
        model = Bank
        fields = ['id', 'name', 'gate_id', 'bank_limit']

class CardSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(required=True, read_only=False)
    # bank = serializers.SlugRelatedField(required=True, read_only=False)
    bank = BankSerializer()

    class Meta:
        model = Card


