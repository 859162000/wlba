from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao_bank_financing.filters import BankFinancingFilterSet
from wanglibao_bank_financing.models import BankFinancing, Bank


class BankFinancingViewSet(PaginatedModelViewSet):
    model = BankFinancing
    filter_class = BankFinancingFilterSet

class BankViewSet(PaginatedModelViewSet):
    model = Bank
