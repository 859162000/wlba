from django.conf.urls import patterns, url

from views import P2PDetailView, audit_product_view

urlpatterns = patterns('',
    url(r'^detail/(?P<id>\w+)', P2PDetailView.as_view(), name='p2p detail'),
    url(r'^audit/(?P<id>\w+)', audit_product_view, name='p2p audit')
)