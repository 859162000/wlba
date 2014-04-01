from django.views.generic import TemplateView
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao_account.permissions import IsAdminUserOrReadOnly
from wanglibao_favorite.models import FavoriteFund
from wanglibao_fund.filters import FundFilterSet
from wanglibao_fund.models import Fund, FundIssuer
from wanglibao_fund.serializers import FundSerializer


class FundViewSet(PaginatedModelViewSet):
    model = Fund
    filter_class = FundFilterSet
    serializer_class = FundSerializer
    permission_classes = (IsAdminUserOrReadOnly,)


class FundIssuerViewSet(PaginatedModelViewSet):
    model = FundIssuer
    permission_classes = (IsAdminUserOrReadOnly,)


class FundHomeView(TemplateView):
    template_name = "fund_home.jade"


class FundDetailView(TemplateView):
    template_name = "fund_detail.jade"

    def get_context_data(self, **kwargs):
        id = kwargs['id']
        context = super(FundDetailView, self).get_context_data(**kwargs)
        is_favorited = 0
        fund=Fund.objects.get(pk=id)
        if self.request.user.is_authenticated():
            if FavoriteFund.objects.filter(user=self.request.user, item=fund).exists():
                is_favorited = 1
        context['is_favorited'] = is_favorited
        context['fund'] = fund
        return context
