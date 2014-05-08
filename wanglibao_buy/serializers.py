from django.utils import timezone
from rest_framework import serializers
from wanglibao_buy.models import TradeInfo


class TradeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeInfo

    created_at = serializers.DateTimeField(default=timezone.now, read_only=True)


