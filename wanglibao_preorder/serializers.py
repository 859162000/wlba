from django.utils import timezone
from rest_framework import serializers
from wanglibao_preorder.models import PreOrder


class PreOrderSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(default=timezone.now, read_only=True)

    class Meta:
        model = PreOrder
