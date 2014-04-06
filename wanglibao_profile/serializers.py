from rest_framework import serializers
from wanglibao_profile.models import WanglibaoUserProfile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = WanglibaoUserProfile

        fields = [
            'nick_name',
            'investment_asset',
            'investment_period',
            'risk_level'
        ]

        read_only_fields = ('nick_name',)
