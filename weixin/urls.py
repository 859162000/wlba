# encoding:utf-8
from django.conf.urls import patterns, url
import views

urlpatterns = patterns(
    '',
    url(r'^connect/(?P<id>\w+)/', views.ConnectView.as_view()),
    url(r'^p2p/list/', views.P2PListView.as_view()),
)
