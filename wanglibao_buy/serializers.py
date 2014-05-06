from django.utils import timezone
from rest_framework import serializers
from wanglibao_buy.models import BuyInfo


class BuyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyInfo

    created_at = serializers.DateTimeField(default=timezone.now, read_only=True)


