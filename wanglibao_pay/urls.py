from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from wanglibao_pay.views import BankListView, PayCallback, WithdrawCompleteView, WithdrawCallback, PayView, WithdrawView, \
    PayCompleteView, WithdrawTransactions

urlpatterns = patterns('',
    url(r'^banks/$', login_required(BankListView.as_view()), name='pay-banks'),
    url(r'^withdraw/$', login_required(WithdrawView.as_view(), login_url='/accounts/register/'), name='withdraw'),
    url(r'^withdraw/complete/$', login_required(WithdrawCompleteView.as_view(), login_url='/accounts/register/'), name='withdraw-complete'),
    url(r'^withdraw/callback/$', WithdrawCallback.as_view(), name='withdraw-callback'),
    url(r'^deposit/$', login_required(PayView.as_view(), login_url='/accounts/register/'), name='deposit-view'),
    url(r'^deposit/callback/$', PayCallback.as_view(), name='deposit-callback'),
    url(r'^deposit/complete/$', login_required(PayCompleteView.as_view(), login_url='/accounts/register/'), name='deposit-callback'),
    url(r'^withdraw/audit/$', login_required(WithdrawTransactions.as_view(), login_url='/accounts/register/'), name='withdraw-transactions'),
)