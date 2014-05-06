from rest_framework import serializers
from wanglibao_profile.models import WanglibaoUserProfile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = WanglibaoUserProfile
        read_only_fields = ('nick_name', 'phone', 'phone_verified')
