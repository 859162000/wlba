#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from views import AnnouncementHomeView, AnnouncementDetailView, AnnouncementPreviewView, \
    AppMemorabiliaHomeView, AppMemorabiliaDetailView, AppMemorabiliaPreviewView


urlpatterns = patterns(
    '',
    url(r'^$', AnnouncementHomeView.as_view(), name='announcement_home'),
    url(r'^detail/(?P<id>\w+)/$', AnnouncementDetailView.as_view(), name='announcement_detail'),
    url(r'^preview/(?P<id>\w+)/$', AnnouncementPreviewView.as_view(), name='announcement_preview'),
)

# APP-大事记
urlpatterns += patterns(
    '',
    url(r'^app_memorabilia/$', AppMemorabiliaHomeView.as_view(), name='app_memorabilia_home'),
    url(r'^app_memorabilia_detail/(?P<id>\w+)/$', AppMemorabiliaDetailView.as_view(), name='app_memorabilia_detail'),
    url(r'^app_memorabilia_preview/(?P<id>\w+)/$', AppMemorabiliaPreviewView.as_view(), name='app_memorabilia_preview'),
)
