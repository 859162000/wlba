#!/usr/bin/env python
# encoding:utf-8

from django.conf.urls import patterns, include, url
from rest_framework.routers import DefaultRouter
from wanglibao_app.views import (AppActivateImageAPIView, AppRepaymentAPIView, AppDayListView, AppGuardView,
                                 AppGuideView, AppSecureView, AppExploreView, AppP2PProductViewSet, AppRecommendViewSet,
                                 SendValidationCodeView, AppIncomeRateAPIView, AppPhoneBookUploadAPIView,
                                 AppPhoneBookQueryAPIView, AppPhoneBookAlertApiView,)

router = DefaultRouter()

router.register(r'investlist', AppP2PProductViewSet)
router.register(r'recommend', AppRecommendViewSet)


# app端改版新接口
urlpatterns = patterns(
    '',
    url(r'', include(router.urls)),
    url(r'^preload/$', AppActivateImageAPIView.as_view()),
    url(r'^repayment/$', AppRepaymentAPIView.as_view()),
    url(r'^guard/$', AppGuardView.as_view()),
    url(r'^guide/$', AppGuideView.as_view()),
    url(r'^daylist/$', AppDayListView.as_view()),
    # url(r'^secure/$', AppSecureView.as_view()),
    url(r'^explore/$', AppExploreView.as_view()),
    url(r'^phone_validation_code/(?P<phone>\d{11})/$', SendValidationCodeView.as_view()),
    url(r'^rate/$', AppIncomeRateAPIView.as_view()),
    url(r'^phone/upload/$', AppPhoneBookUploadAPIView.as_view()),
    url(r'^phone/query/$', AppPhoneBookQueryAPIView.as_view()),
    url(r'^phone/alert/$', AppPhoneBookAlertApiView.as_view()),
)
