from rest_framework import serializers
from wanglibao_pay.models import Card, Bank

class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ['id', 'name', 'gate_id', ]

class CardSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(required=True, read_only=False)
    # bank = serializers.SlugRelatedField(required=True, read_only=False)
    bank = BankSerializer()

    class Meta:
        model = Card


