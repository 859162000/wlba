# encoding:utf-8

from django.http import Http404
from django.views.generic import TemplateView
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao_favorite.models import FavoriteFund
from wanglibao_fund.filters import FundFilterSet
from wanglibao_fund.models import Fund, FundIssuer
from wanglibao_fund.serializers import FundSerializer
from wanglibao_hotlist.models import HotFund
from wanglibao_announcement.utility import Announcementfund


class FundViewSet(PaginatedModelViewSet):
    model = Fund
    filter_class = FundFilterSet
    serializer_class = FundSerializer
    permission_classes = (IsAdminUserOrReadOnly,)

    def get_queryset(self):
        return Fund.objects.exclude(availablefund__isnull=True).prefetch_related('issuer')


class FundIssuerViewSet(PaginatedModelViewSet):
    model = FundIssuer
    permission_classes = (IsAdminUserOrReadOnly,)


class FundProductsView(TemplateView):
    template_name = "fund_products.jade"

    def get_context_data(self, **kwargs):

        return {
            'hot_funds': HotFund.objects.all().prefetch_related('fund').prefetch_related('fund__issuer')[:3],
            'announcements': Announcementfund
        }


class FundDetailView(TemplateView):
    template_name = "fund_detail.jade"

    def get_context_data(self, **kwargs):
        id = kwargs['id']
        context = super(FundDetailView, self).get_context_data(**kwargs)
        is_favorited = 0
        try:
            fund = Fund.objects.get(pk=id)
        except Fund.DoesNotExist:
            raise Http404(u'您查找的产品不存在')

        if self.request.user.is_authenticated():
            if FavoriteFund.objects.filter(user=self.request.user, item=fund).exists():
                is_favorited = 1
        context['is_favorited'] = is_favorited
        context['fund'] = fund
        if fund.type == u'货币型':
            self.template_name = 'monetary_fund_detail.jade'
        else:
            self.template_name = 'fund_detail.jade'

        context['announcements'] = Announcementfund

        return context
