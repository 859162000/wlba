from django.conf.urls import patterns, url
from wanglibao_preorder.views import PreOrderP2PView


urlpatterns = patterns(
    '',
    url(r'^p2p', PreOrderP2PView.as_view()),
    )