#!/usr/bin/env python
# encoding:utf-8

from django.conf.urls import patterns, url
<<<<<<< HEAD
from views import HomeView, TestView
=======
from django.views.generic import TemplateView, RedirectView
from views import HomeView
>>>>>>> 9eae1c7ce9be2683bee381de64c1ac7756b04ee0

urlpatterns = patterns('',
    #url(r'^detail/(?P<id>\w+)', P2PDetailView.as_view(), name='p2p detail'),
    url(r'^$', HomeView.as_view(), name='home'),
<<<<<<< HEAD
    url(r'^test/$', TestView.as_view(), name='test'),
=======
    url(r'^mobile_index/$', TemplateView.as_view(template_name="mobile_index.jade")),
    url(r'^mobile_assets/$', TemplateView.as_view(template_name="mobile_assets.jade")),
    url(r'^mobile_more/$', TemplateView.as_view(template_name="mobile_more.jade")),
    url(r'^mobile_detail/$', TemplateView.as_view(template_name="mobile_detail.jade")),
>>>>>>> 9eae1c7ce9be2683bee381de64c1ac7756b04ee0
)
