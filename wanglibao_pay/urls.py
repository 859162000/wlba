#!/usr/bin/env python
# encoding:utf-8

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from wanglibao_pay.views import BankListView, PayCallback, WithdrawCompleteView, WithdrawCallback, PayView, WithdrawView, \
    PayCompleteView, WithdrawTransactions, WithdrawRedirectView, YeeProxyPayCompleteView, BankListForRegisterView

urlpatterns = patterns('',
    # tmplate view
    url(r'^banks/$', login_required(BankListView.as_view()), name='pay-banks'),
    url(r'^banks_for_register/$', login_required(BankListForRegisterView.as_view())),
    url(r'^withdraw/$', login_required(WithdrawView.as_view(), login_url='/accounts/login/'), name='withdraw'),
    url(r'^withdraw/complete/$', login_required(WithdrawCompleteView.as_view(), login_url='/accounts/login/'), name='withdraw-complete'),
    url(r'^withdraw/complete/(?P<result>.*)/$', login_required(WithdrawRedirectView.as_view(), login_url='/accounts/login/'), name='withdraw-complete-result'),
    url(r'^withdraw/callback/$', WithdrawCallback.as_view(), name='withdraw-callback'),
    url(r'^deposit/$', login_required(PayView.as_view(), login_url='/accounts/login/'), name='deposit-view'),
    url(r'^deposit/callback/$', PayCallback.as_view(), name='deposit-callback'),
    url(r'^deposit/complete/$', login_required(PayCompleteView.as_view(), login_url='/accounts/login/'), name='deposit-callback'),
    # todo 在setting中使用名字来引用
    url(r'^deposit/yee_proxy_pay_complete/$', YeeProxyPayCompleteView.as_view()),
    url(r'^withdraw/audit/$', login_required(WithdrawTransactions.as_view(), login_url='/accounts/login/'), name='withdraw-transactions'),
    url(r'^withdraw/rollback/$', login_required(WithdrawTransactions.as_view(), login_url='/accounts/login/'), name='withdraw-rollback'),

    #
)
