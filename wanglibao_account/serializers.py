from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from wanglibao_profile.serializers import ProfileSerializer
from wanglibao_p2p.models import P2PEquity

class UserSerializer (ModelSerializer):
    wanglibaouserprofile = ProfileSerializer()

    """
    The user serializer for wanglibao user resource
    """
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'date_joined', 'wanglibaouserprofile')



