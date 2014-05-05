from rest_framework.serializers import ModelSerializer
from wanglibao_banner.models import Banner


class BannerSerializer(ModelSerializer):
    class Meta:
        model = Banner