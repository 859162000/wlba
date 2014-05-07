from rest_framework import serializers
from wanglibao_hotlist.models import HotTrust, HotFinancing, HotFund, MobileMainPage


class HotTrustSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HotTrust
        depth = 2


class HotFinancingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HotFinancing
        depth = 1


class HotFundSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HotFund
        depth = 3


class MobileHotFundSerializer(HotFundSerializer):
    pass


class MobileHotTrustSerializer(HotTrustSerializer):
    pass


class MobileMainPageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MobileMainPage
        depth = 3
