from django.views.generic import TemplateView
from rest_framework import viewsets
from trust.filters import TrustFilterSet
from trust.models import Trust, Issuer
from wanglibao_rest.serializers import TrustSerializer


class TrustHomeView(TemplateView):

    template_name = "trust_home.html"

    def get_context_data(self, **kwargs):
        context = super(TrustHomeView, self).get_context_data(**kwargs)

        latest_trusts = Trust.objects.order_by('-issue_date')[0:10] # TODO make this value configurable
        context['latest_trusts'] = latest_trusts
        return context


class TrustProductsView(TemplateView):
    template_name = "trust_products.html"


class TrustDetailView(TemplateView):
    template_name = "trust_detail.html"

    def get_context_data(self, **kwargs):
        id = kwargs['id']
        context = super(TrustDetailView, self).get_context_data(**kwargs)
        context['trust'] = Trust.objects.get(pk=id)
        return context


class TrustViewSet(viewsets.ModelViewSet):
    model = Trust
    filter_class = TrustFilterSet
    serializer_class = TrustSerializer
    paginate_by = 20
    paginate_by_param = 'page_size'
    max_paginate_by = 100


class IssuerViewSet(viewsets.ModelViewSet):
    model = Issuer
    paginate_by = 20
    paginate_by_param = 'page_size'
    max_paginate_by = 100
