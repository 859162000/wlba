# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url
from wanglibao_sms.views import SendSMSNoticeAPIView

urlpatterns = patterns(
    '',
    url(r'^send_notice/', SendSMSNoticeAPIView().as_view(), name='send-sms-notice'),
)
