from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ModelViewSet
from wanglibao_portfolio.models import ProductType, Portfolio, UserPortfolio


class PortfolioViewSet(ModelViewSet):
    model = Portfolio


class UserPortfolioViewSet(ModelViewSet):
    model = UserPortfolio


class ProductTypeViewSet(ModelViewSet):
    model = ProductType
