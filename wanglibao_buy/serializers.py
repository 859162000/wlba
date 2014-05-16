from django.utils import timezone
from rest_framework import serializers
from wanglibao_buy.models import TradeInfo, AvailableFund, DailyIncome


class TradeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeInfo
        exclude = 'user',

    created_at = serializers.DateTimeField(default=timezone.now, read_only=True)


class AvailableFundSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableFund


class DailyIncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyIncome
        exclude = ('user', 'url', 'id')
