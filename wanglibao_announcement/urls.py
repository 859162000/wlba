#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from views import (AnnouncementHomeView, AnnouncementDetailView, AnnouncementPreviewView, AnnouncementHomeApi,
                   AnnouncementHasNewestApi)
from django.views.generic import TemplateView

urlpatterns = patterns(
    '',
    url(r'^$', AnnouncementHomeView.as_view(), name='announcement_home'),
    url(r'^detail/(?P<id>\w+)/$', AnnouncementDetailView.as_view(), name='announcement_detail'),
    url(r'^preview/(?P<id>\w+)/$', AnnouncementPreviewView.as_view(), name='announcement_preview'),
    url(r'^list/$', AnnouncementHomeApi.as_view(), name='announcement_list'),
    url(r'^has_newest/(?P<id>\d+)/$', AnnouncementHasNewestApi.as_view(), name='announcement_has_newest'),

    #app公告

    url(r'^risk/$', TemplateView.as_view(template_name="client_announcement_risk.jade")),
    url(r'^safe/$', TemplateView.as_view(template_name="client_announcement_safe.jade")),
    url(r'^reward/$', TemplateView.as_view(template_name="client_announcement_reward.jade")),
    url(r'^qiye/$', TemplateView.as_view(template_name="client_announcement_qiye.jade")),
    url(r'^rock/$', TemplateView.as_view(template_name="client_announcement_rock.jade")),
    url(r'^trading-A/$', TemplateView.as_view(template_name="client_announcement_trading_A.jade")),
    url(r'^trading-B/$', TemplateView.as_view(template_name="client_announcement_trading_B.jade")),
    url(r'^abc-pay/$', TemplateView.as_view(template_name="client_announcement_abc_pay.jade")),
)
