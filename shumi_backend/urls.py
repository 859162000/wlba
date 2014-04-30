from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from views import OAuthCallbackView, GetAuthorizeStatusView

urlpatterns = patterns('',
    url(r'^callback/(?P<pk>\d+)/$', OAuthCallbackView.as_view(), name='callback-view'),
    url(r'^get_auth_status/', login_required(GetAuthorizeStatusView.as_view()), name='get_auth_status-view'),
)