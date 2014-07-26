from rest_framework import serializers
from wanglibao_hotlist.models import HotTrust, HotFinancing, HotFund, MobileMainPage, MobileMainPageP2P
from wanglibao_p2p.serializers import P2PProductSerializer


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


class MobileMainPageP2PSerializer(serializers.HyperlinkedModelSerializer):
    item = serializers.SerializerMethodField('get_item')

    class Meta:
        model = MobileMainPageP2P
        depth = 2

    def get_item(self, obj):
        serializer = P2PProductSerializer(obj.item, context=self.context)
        return serializer.data

