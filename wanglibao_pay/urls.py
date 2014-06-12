from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from wanglibao_pay.views import BankListView, PayCallback

urlpatterns = patterns('',
    url(r'^banks/$', login_required(BankListView.as_view()), name='pay-banks'),
    url(r'^callback/', PayCallback.as_view(), name='pay-callback'),
)