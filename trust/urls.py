from django.conf.urls import patterns, url
from trust.views import TrustHomeView, TrustDetailView


urlpatterns = patterns(
    '',
    url(r'^home/', TrustHomeView.as_view(), name="trust_home"),
    url(r'^detail/(?P<id>\w+)', TrustDetailView.as_view(), name="trust_detail"),
)
