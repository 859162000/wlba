from django.conf.urls import patterns, url

from views import P2PDetailView

urlpatterns = patterns('',
    url(r'^detail/(?P<id>\w+)', P2PDetailView.as_view(), name='p2p detail'),
)