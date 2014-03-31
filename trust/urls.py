from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from trust.views import TrustHomeView, TrustProductsView, TrustDetailView

urlpatterns = patterns(
    '',
    url(r'^home/', TrustHomeView.as_view(), name="trust_home"),
    url(r'^products/', TrustProductsView.as_view(), name="trust_product"),
    url(r'^companies/', TemplateView.as_view(template_name="trust_company.jade"), name="trust_company"),
    url(r'^detail/(?P<id>\w+)', TrustDetailView.as_view(), name="trust_detail"),
)
