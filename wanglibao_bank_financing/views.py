from django.views.generic import TemplateView
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao.views import IsAdminUserOrReadOnly
from wanglibao_bank_financing.filters import BankFinancingFilterSet
from wanglibao_bank_financing.models import BankFinancing, Bank
from wanglibao_bank_financing.serializers import BankFinancingSerializer, BankSerializer


class BankFinancingViewSet(PaginatedModelViewSet):
    model = BankFinancing
    filter_class = BankFinancingFilterSet
    serializer_class = BankFinancingSerializer
    permission_classes = (IsAdminUserOrReadOnly,)


class BankViewSet(PaginatedModelViewSet):
    model = Bank
    serializer_class = BankSerializer
    permission_classes = (IsAdminUserOrReadOnly,)


class FinancingHomeView(TemplateView):
    template_name = "financing_home.jade"


class FinancingProductsView(TemplateView):
    template_name = "financing_products.jade"