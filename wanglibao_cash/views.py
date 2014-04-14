# encoding: utf-8

from django.http import Http404
from django.views.generic import TemplateView
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao_account.permissions import IsAdminUserOrReadOnly
from wanglibao_cash.filters import CashFilterSet
from wanglibao_cash.models import Cash, CashIssuer
from wanglibao_cash.serializers import CashSerializer, CashIssuerSerializer
from wanglibao_favorite.models import FavoriteCash


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


class CashDetailView(TemplateView):
    template_name = "cash_detail.jade"

    def get_context_data(self, **kwargs):
        id = kwargs['id']
        context = super(CashDetailView, self).get_context_data(**kwargs)
        try:
            cash = Cash.objects.get(pk=id)
        except Cash.DoesNotExist:
            raise Http404(u'您查找的产品不存在')

        is_favorited = 0
        if self.request.user.is_authenticated():
            if FavoriteCash.objects.filter(item=cash, user=self.request.user).exists():
                is_favorited = 1
        context['is_favorited'] = is_favorited
        context['cash'] = cash
        return context
