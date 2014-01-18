from rest_framework.serializers import ModelSerializer
from wanglibao_portfolio.models import Portfolio, UserPortfolio


class PortfolioSerializer(ModelSerializer):
    """
    The serializer which serialize the portfolio object
    """
    class Meta:
        model = Portfolio


class UserPortfolioSerializer(ModelSerializer):
    class Meta:
        model = UserPortfolio


