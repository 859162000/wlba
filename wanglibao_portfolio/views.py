from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao_portfolio.filters import PortfolioFilterSet
from wanglibao_portfolio.models import ProductType, Portfolio, UserPortfolio
from wanglibao_portfolio.serializers import PortfolioSerializer


class PortfolioViewSet(PaginatedModelViewSet):
    model = Portfolio
    serializer_class = PortfolioSerializer
    filter_class = PortfolioFilterSet
    permission_classes = (IsAdminUserOrReadOnly,)


class UserPortfolioViewSet(ModelViewSet):
    model = UserPortfolio
    permission_classes = (IsAuthenticated,)


class ProductTypeViewSet(ModelViewSet):
    model = ProductType
    permission_classes = (IsAdminUser,)


class PortfolioHomeView(TemplateView):
    template_name = "consult.jade"
