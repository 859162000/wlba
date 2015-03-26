#!/usr/bin/env python
# encoding:utf-8

from django.conf.urls import patterns, url
from views import HomeView, TestView

urlpatterns = patterns('',
    #url(r'^detail/(?P<id>\w+)', P2PDetailView.as_view(), name='p2p detail'),
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^test/$', TestView.as_view(), name='test'),
)
