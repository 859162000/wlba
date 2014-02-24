from rest_framework import serializers
from wanglibao_preorder.models import PreOrder


class PreOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreOrder
