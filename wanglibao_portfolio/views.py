from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ModelViewSet
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao_portfolio.filters import PortfolioFilterSet
from wanglibao_portfolio.models import ProductType, Portfolio, UserPortfolio
from wanglibao_portfolio.serializers import PortfolioSerializer


class PortfolioViewSet(PaginatedModelViewSet):
    model = Portfolio
    serializer_class = PortfolioSerializer
    filter_class = PortfolioFilterSet


class UserPortfolioViewSet(ModelViewSet):
    model = UserPortfolio


class ProductTypeViewSet(ModelViewSet):
    model = ProductType
