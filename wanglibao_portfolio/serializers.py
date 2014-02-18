from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from wanglibao_portfolio.models import Portfolio, UserPortfolio, PortfolioProductEntry, ProductType


class ProductTypeSerializer(ModelSerializer):
    class Meta:
        model = ProductType


class PortfolioProductEntrySerializer(ModelSerializer):
    product = ProductTypeSerializer()

    class Meta:
        model = PortfolioProductEntry

class PortfolioSerializer(ModelSerializer):
    """
    The serializer which serialize the portfolio object
    """

    products = PortfolioProductEntrySerializer(many=True)

    class Meta:
        model = Portfolio
        depth = 1


class UserPortfolioSerializer(ModelSerializer):
    class Meta:
        model = UserPortfolio


