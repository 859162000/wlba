from rest_framework import serializers
from wanglibao_pay.models import Card


class CardSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(required=True, read_only=False)
    bank = serializers.PrimaryKeyRelatedField(required=True, read_only=False)

    class Meta:
        model = Card
