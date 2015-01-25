from django.conf.urls import patterns, url
from views import P2PDetailView, audit_product_view, P2PListView, preview_contract, copy_product_view,\
    audit_amortization_view, audit_equity_view

urlpatterns = patterns('',
    url(r'^detail/(?P<id>\w+)', P2PDetailView.as_view(), name='p2p detail'),
    url(r'^audit/(?P<id>\w+)', audit_product_view, name='p2p audit'),
    url(r'^equitydetail/(?P<id>\w+)', audit_equity_view, name='p2p audit equity'),
    url(r'^amortizationdetail/(?P<id>\w+)', audit_amortization_view, name='p2p audit amortization'),
    url(r'^copy/(?P<id>\w+)', copy_product_view, name='p2p copy'),
    url(r'^list', P2PListView.as_view(), name='p2p_list'),
    url(r'^contract_preview/(?P<id>\w+)/', preview_contract),
)