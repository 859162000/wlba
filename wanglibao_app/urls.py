#!/usr/bin/env python
# encoding:utf-8

from django.conf.urls import patterns, include, url
from wanglibao_app.views import (AppActivateImageAPIView, AppRepaymentAPIView, AppDayListView, AppGuardView,
                                 AppGuideView, AppSecureView, AppExploreView)


# app端改版新接口
urlpatterns = patterns(
    '',
    url(r'^preload/$', AppActivateImageAPIView.as_view()),
    url(r'^repayment/$', AppRepaymentAPIView.as_view()),
    url(r'^guard/$', AppGuardView.as_view()),
    url(r'^guide/$', AppGuideView.as_view()),
    url(r'^daylist/$', AppDayListView.as_view()),
    url(r'^secure/$', AppSecureView.as_view()),
    url(r'^explore/$', AppExploreView.as_view()),
)
