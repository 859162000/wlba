from django.shortcuts import render

# Create your views here.
from django.db.models import Q
from django.utils import timezone
from django.views.generic import TemplateView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao_portfolio.filters import PortfolioFilterSet
from wanglibao_portfolio.models import ProductType, Portfolio, UserPortfolio
from wanglibao_portfolio.serializers import PortfolioSerializer
from wanglibao_announcement.models import Announcement


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

    def get_context_data(self, **kwargs):

        Announcements = Announcement.objects.filter(starttime__lte=timezone.now(), endtime__gte=timezone.now())\
            .filter(type='all').filter(status=1).order_by('-priority')[:1]

        return {
            'announcements': Announcements
        }
