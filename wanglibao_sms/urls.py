# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from views import AchievedMessages, ReportMessages, ArriveRate

urlpatterns = patterns(
    '',

    url(r'^api/sms/achieved/$', AchievedMessages.as_view(), name='arrive_rate'),
    url(r'^api/sms/report/$', ReportMessages.as_view(), name='arrive_rate'),
    # url(r'^api/sms/arrive_rate/$', login_required(ArriveRate.as_view(),
    #                                               login_url='/accounts/login/'), name='arrive_rate'),
    # url(r'^api/sms/message/edit/$', login_required(ArriveRate.as_view(),
    #                                                login_url='/accounts/login/'), name='message_for_admin'),
)
