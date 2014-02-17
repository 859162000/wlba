from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao_bank_financing.filters import BankFinancingFilterSet
from wanglibao_bank_financing.models import BankFinancing, Bank
from wanglibao_bank_financing.serializers import BankFinancingSerializer


class BankFinancingViewSet(PaginatedModelViewSet):
    model = BankFinancing
    filter_class = BankFinancingFilterSet
    serializer_class = BankFinancingSerializer

class BankViewSet(PaginatedModelViewSet):
    model = Bank
