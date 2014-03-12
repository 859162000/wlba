from django.views.generic import TemplateView
from rest_framework import viewsets
from trust.filters import TrustFilterSet
from trust.models import Trust, Issuer
from serializers import TrustSerializer
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao.views import IsAdminUserOrReadOnly


class TrustHomeView(TemplateView):

    template_name = "trust_home.jade"

    def get_context_data(self, **kwargs):
        context = super(TrustHomeView, self).get_context_data(**kwargs)

        latest_trusts = Trust.objects.order_by('-issue_date')[0:10] # TODO make this value configurable
        context['latest_trusts'] = latest_trusts
        return context


class TrustProductsView(TemplateView):
    template_name = "trust_products.jade"


class TrustDetailView(TemplateView):
    template_name = "trust_detail.jade"

    def get_context_data(self, **kwargs):
        id = kwargs['id']
        context = super(TrustDetailView, self).get_context_data(**kwargs)
        context['trust'] = Trust.objects.get(pk=id)
        return context


class TrustViewSet(PaginatedModelViewSet):
    model = Trust
    filter_class = TrustFilterSet
    serializer_class = TrustSerializer
    permission_classes = (IsAdminUserOrReadOnly,)


class IssuerViewSet(PaginatedModelViewSet):
    model = Issuer
    permission_classes = (IsAdminUserOrReadOnly,)
