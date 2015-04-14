#!/usr/bin/env python
# encoding:utf-8

from django.conf.urls import patterns, url
from views import HomeView, IndexView, DetailView
from django.views.generic import TemplateView, RedirectView
from views import HomeView

urlpatterns = patterns('',
    #url(r'^detail/(?P<id>\w+)', P2PDetailView.as_view(), name='p2p detail'),
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^home/$', HomeView.as_view(), name='homde'),
    url(r'^detail/(?P<id>\w+)', DetailView.as_view(), name='mobile p2p detail'),
    url(r'^mobile_index/$', TemplateView.as_view(template_name="mobile_index.jade")),
    url(r'^mobile_assets/$', TemplateView.as_view(template_name="mobile_assets.jade")),
    url(r'^mobile_more/$', TemplateView.as_view(template_name="mobile_more.jade")),
    url(r'^mobile_detail/$', TemplateView.as_view(template_name="mobile_detail.jade")),
    url(r'^weixin_index/$', TemplateView.as_view(template_name="weixin_index.jade")),
    url(r'^weixin_inputt/$', TemplateView.as_view(template_name="weixin_inputt.jade")),
    url(r'^weixin_about/$', TemplateView.as_view(template_name="weixin_about.jade")),
     url(r'^weixin_fee/$', TemplateView.as_view(template_name="weixin_fee.jade")),

)
