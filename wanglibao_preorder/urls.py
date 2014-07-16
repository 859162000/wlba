from django.conf.urls import patterns, url
from wanglibao_preorder.views import PreOrderP2PView, PreOrderP2PPhoneView


urlpatterns = patterns(
    '',
    url(r'^p2p/$', PreOrderP2PView.as_view()),
    url(r'^p2p-phone/$', PreOrderP2PPhoneView.as_view()),
    )