from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from views import OAuthCallbackView, OAuthTriggerView

urlpatterns = patterns('',
    url(r'^callback/(?P<pk>\d+)/$', OAuthCallbackView.as_view(), name='oauth-callback-view'),
    url(r'^test/trigger/', login_required(OAuthTriggerView.as_view()), name='test-trigger-view'),
)