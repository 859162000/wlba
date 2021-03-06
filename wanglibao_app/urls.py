#!/usr/bin/env python
# encoding:utf-8

from django.conf.urls import patterns, include, url
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from wanglibao_app.views import (AppActivateImageAPIView, AppRepaymentAPIView, AppDayListView, AppGuardView,
                                 AppGuideView, AppSecureView, AppExploreView, AppP2PProductViewSet, AppRecommendViewSet,
                                 SendValidationCodeView, AppIncomeRateAPIView, AppPhoneBookUploadAPIView,
                                 AppPhoneBookQueryAPIView, AppPhoneBookAlertApiView, AppInviteAllGoldAPIView,
                                 AppAboutView, AppManagementView, AppLogoutAPIView, AppQuestionsView,
                                 AppQuestionsResultView, AppCostView, SendValidationCodeNoCaptchaView,
                                 AppRepaymentPlanAllAPIView, AppRepaymentPlanMonthAPIView, AppAreaView,
                                 AppAreaApiView, AppMemorabiliaView, AppDataModuleView, AppActivateScoreImageAPIView,
                                 AppFinanceView, AppPraiseAwardView, AppCheckInView, AppMemorabiliaDetailView,
                                 AppRecommendAPIView)
from wanglibao_account.views import MarginRecordsAPIView
router = DefaultRouter()

router.register(r'investlist', AppP2PProductViewSet)
router.register(r'recommend', AppRecommendViewSet)


# app端改版新接口
urlpatterns = patterns(
    '',
    url(r'', include(router.urls)),
    url(r'^recommend_new/$', AppRecommendAPIView.as_view()),
    url(r'^preload/$', AppActivateImageAPIView.as_view()),
    url(r'^preload_score/$', AppActivateScoreImageAPIView.as_view()),
    url(r'^repayment/$', AppRepaymentAPIView.as_view()),
    url(r'^repayment_plan/all/$', AppRepaymentPlanAllAPIView.as_view()),
    url(r'^repayment_plan/month/$', AppRepaymentPlanMonthAPIView.as_view()),
    url(r'^guard/$', AppGuardView.as_view()),
    url(r'^guide/$', AppGuideView.as_view()),
    url(r'^daylist/$', AppDayListView.as_view()),
    url(r'^explore/$', AppExploreView.as_view()),
    url(r'^about/$', AppAboutView.as_view()),
    url(r'^team/$', AppManagementView.as_view()),
    url(r'^phone_validation_code/(?P<phone>\d{11})/$', SendValidationCodeView.as_view()),  # APP注册短信验证码
    url(r'^phone_validation_code_no_captcha/(?P<phone>\d{11})/$', SendValidationCodeNoCaptchaView.as_view()),  # 提现短信验证码
    url(r'^rate/$', AppIncomeRateAPIView.as_view()),
    url(r'^phone/upload/$', AppPhoneBookUploadAPIView.as_view()),
    url(r'^phone/query/$', AppPhoneBookQueryAPIView.as_view()),
    url(r'^phone/alert/$', AppPhoneBookAlertApiView.as_view()),
    url(r'^phone/invite/broker/$', AppInviteAllGoldAPIView.as_view()),
    url(r'^logout/$', AppLogoutAPIView.as_view()),
    url(r'^questions/$', AppQuestionsView.as_view()),
    url(r'^questions/(?P<index>\w+)/$', AppQuestionsResultView.as_view()),
    url(r'^cost/$', AppCostView.as_view()),

    url(r'^area/$', AppAreaView.as_view()),
    url(r'^area/fetch/$', AppAreaApiView.as_view()),
    url(r'^app_memorabilia/$', AppMemorabiliaView.as_view(), name='app_memorabilia'),
    url(r'^memorabilia/detail/(?P<id>\d+)/$', AppMemorabiliaDetailView.as_view()),

    url(r'^data_cube/$', AppDataModuleView.as_view()),#数据魔方
    url(r'^finance/$', AppFinanceView.as_view()),
    url(r'^share-finance/$', TemplateView.as_view(template_name="client_share_finance.jade"), name='app_finance'),
    url(r'^praise-award/$', AppPraiseAwardView.as_view()),
    url(r'^check-in/$', AppCheckInView.as_view()),
    url(r'^check-in-share/$', TemplateView.as_view(template_name="client_checkIn_share.jade"), name='client_checkIn_share'),

    # 用户账户流水
    url(r'^margin_records/$', MarginRecordsAPIView.as_view()),
)

