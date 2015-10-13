# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

urlpatterns = patterns(
    '',

    # url(r'^api/sms/arrive_rate/$', login_required(ArriveRate.as_view(),
    #                                               login_url='/accounts/login/'), name='arrive_rate'),
    # url(r'^api/sms/message/edit/$', login_required(ArriveRate.as_view(),
    #                                                login_url='/accounts/login/'), name='message_for_admin'),
)
