# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt
from .views import AccessTokenView, AccessTokenOauthView


urlpatterns = patterns(
    '',
    url('^(?P<grant_type>(access_token|refresh_token))/$',
        csrf_exempt(AccessTokenView.as_view()),
        name='oauth2_access_token'),

    url('^auth/$', AccessTokenOauthView.as_view(),
        name='oauth2_token_auth'),
)
