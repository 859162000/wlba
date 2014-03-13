from django.views.generic import TemplateView
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao.views import IsAdminUserOrReadOnly
from wanglibao_cash.filters import CashFilterSet
from wanglibao_cash.models import Cash, CashIssuer
from wanglibao_cash.serializers import CashSerializer, CashIssuerSerializer


class CashViewSet(PaginatedModelViewSet):
    model = Cash
    filter_class = CashFilterSet
    serializer_class = CashSerializer
    permission_classes = (IsAdminUserOrReadOnly,)


class CashIssuerViewSet(PaginatedModelViewSet):
    model = CashIssuer
    serializer_class = CashIssuerSerializer
    permission_classes = (IsAdminUserOrReadOnly,)


class CashHomeView(TemplateView):
    template_name = "cash_home.jade"
