# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url
from wanglibao_sms.views import RequestSendSMSAPIView

urlpatterns = patterns(
    '',
    url(r'^send/', RequestSendSMSAPIView().as_view(), name='send sms from request'),
)
