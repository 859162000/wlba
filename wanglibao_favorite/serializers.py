from rest_framework import serializers
from wanglibao_favorite.models import FavoriteTrust, FavoriteFund, FavoriteFinancing


class FavoriteBaseSerializer(serializers.ModelSerializer):
    class Meta:
        depth = 1
        exclude = ('user',)


class FavoriteTrustSerializer(FavoriteBaseSerializer):
    class Meta(FavoriteBaseSerializer.Meta):
        model = FavoriteTrust


class FavoriteFundSerializer(FavoriteBaseSerializer):
    class Meta(FavoriteBaseSerializer.Meta):
        model = FavoriteFund


class FavoriteFinancingSerializer(FavoriteBaseSerializer):
    class Meta(FavoriteBaseSerializer.Meta):
        model = FavoriteFinancing
