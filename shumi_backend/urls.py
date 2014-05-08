from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from views import OAuthCallbackView, OAuthTriggerView, OAuthStatusView, OAuthStartView, TradeView, TradeCallbackView

urlpatterns = patterns('',
    url(r'^oauth/callback/(?P<pk>\d+)/$', OAuthCallbackView.as_view(), name='oauth-callback-view'),
    url(r'^oauth/check_oauth_status/$', login_required(OAuthStatusView.as_view()), name='oauth-status-view'),
    url(r'^oauth/start_oauth/', login_required(OAuthStartView.as_view()), name='oauth-start-view'),
    url(r'^trade/redirect/', login_required(TradeView.as_view()), name='trade-redirect-view'),
    url(r'^trade/callback/', login_required(TradeCallbackView.as_view()), name='trade-callback-view'),
    url(r'^trade/trigger/', login_required(OAuthTriggerView.as_view()), name='test-trigger-view'),
)