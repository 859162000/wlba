from rest_framework import serializers
from wanglibao_hotlist.models import HotTrust, HotFinancing, HotFund


class HotTrustSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HotTrust
        depth = 1


class HotFinancingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HotFinancing
        depth = 1


class HotFundSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HotFund
        depth = 3