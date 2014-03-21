from django.views.generic import TemplateView
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao.views import IsAdminUserOrReadOnly
from wanglibao_bank_financing.filters import BankFinancingFilterSet
from wanglibao_bank_financing.models import BankFinancing, Bank
from wanglibao_bank_financing.serializers import BankFinancingSerializer, BankSerializer
from wanglibao_favorite.models import FavoriteFinancing


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


class FinancingDetailView(TemplateView):
    template_name = "financing_detail.jade"

    def get_context_data(self, id, **kwargs):
        financing = BankFinancing.objects.get(pk=id)
        is_favorited = 0
        if self.request.user.is_authenticated():
            if FavoriteFinancing.objects.filter(user=self.request.user, item=financing).exists():
                is_favorited = 1

        return {
            'financing': financing,
            'is_favorited': is_favorited
        }
