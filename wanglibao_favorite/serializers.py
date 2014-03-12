from rest_framework import serializers
from trust.serializers import TrustSerializer
from wanglibao_bank_financing.serializers import BankFinancingSerializer
from wanglibao_favorite.models import FavoriteTrust, FavoriteFund, FavoriteFinancing
from wanglibao_fund.serializers import FundSerializer


class FavoriteBaseSerializer(serializers.ModelSerializer):
    class Meta:
        depth = 1
        exclude = ('user',)


class FavoriteTrustSerializer(FavoriteBaseSerializer):
    item = TrustSerializer()

    class Meta(FavoriteBaseSerializer.Meta):
        model = FavoriteTrust


class FavoriteFundSerializer(FavoriteBaseSerializer):
    item = FundSerializer()

    class Meta(FavoriteBaseSerializer.Meta):
        model = FavoriteFund


class FavoriteFinancingSerializer(FavoriteBaseSerializer):
    item = BankFinancingSerializer()

    class Meta(FavoriteBaseSerializer.Meta):
        model = FavoriteFinancing
