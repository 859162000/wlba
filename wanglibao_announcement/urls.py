#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from views import AnnouncementHomeView, AnnouncementDetailView, AnnouncementPreviewView
from django.views.generic import TemplateView

urlpatterns = patterns(
    '',
    url(r'^$', AnnouncementHomeView.as_view(), name='announcement_home'),
    url(r'^detail/(?P<id>\w+)/$', AnnouncementDetailView.as_view(), name='announcement_detail'),
    url(r'^preview/(?P<id>\w+)/$', AnnouncementPreviewView.as_view(), name='announcement_preview'),

    #app公告

    url(r'^risk/$', TemplateView.as_view(template_name="client_announcement_risk.jade")),
    url(r'^safe/$', TemplateView.as_view(template_name="client_announcement_safe.jade")),
    url(r'^reward/$', TemplateView.as_view(template_name="client_announcement_reward.jade")),
)
