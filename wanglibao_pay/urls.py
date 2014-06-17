from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from wanglibao_pay.views import BankListView, PayCallback, WithdrawCompleteView, WithdrawCallback

urlpatterns = patterns('',
    url(r'^banks/$', login_required(BankListView.as_view()), name='pay-banks'),
    url(r'^withdraw/$', TemplateView.as_view(template_name="withdraw.jade"), name='withdraw'),
    url(r'^withdraw/complete/$', WithdrawCompleteView.as_view(), name='withdraw-complete'),
    url(r'^pay/callback/', PayCallback.as_view(), name='pay-callback'),
    url(r'^withdraw/callback/', WithdrawCallback.as_view(), name='withdraw-callback'),
)