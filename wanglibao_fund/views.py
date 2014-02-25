from django.views.generic import TemplateView
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao_fund.filters import FundFilterSet
from wanglibao_fund.models import Fund, FundIssuer
from wanglibao_fund.serializers import FundSerializer


class FundViewSet(PaginatedModelViewSet):
    model = Fund
    filter_class = FundFilterSet
    serializer_class = FundSerializer


class FundIssuerViewSet(PaginatedModelViewSet):
    model = FundIssuer


class FundHomeView(TemplateView):
    template_name = "fund_home.jade"
