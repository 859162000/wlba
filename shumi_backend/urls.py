from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from views import OAuthCallbackView, OAuthTriggerView, OAuthStatusView, OAuthStartView

urlpatterns = patterns('',
    url(r'^callback/(?P<pk>\d+)/$', OAuthCallbackView.as_view(), name='oauth-callback-view'),
    url(r'^test/trigger/', login_required(OAuthTriggerView.as_view()), name='test-trigger-view'),
    url(r'^check_oauth_status/(?P<pk>\d+)/$', login_required(OAuthStatusView.as_view()), name='oauth-status-view'),
    url(r'^start_oauth/', login_required(OAuthStartView.as_view()), name='oauth-start-view'),
)