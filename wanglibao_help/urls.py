#!/usr/bin/env python
# encoding:utf-8

from django.conf.urls import patterns, url
from views import HelpView

urlpatterns = patterns('',
    #url(r'^detail/(?P<id>\w+)', P2PDetailView.as_view(), name='p2p detail'),
    url(r'^$', HelpView.as_view(), name='help'),
)
