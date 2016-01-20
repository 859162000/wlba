# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt
from .views import AccessTokenView, TokenLoginOpenApiView, TokenLoginOpenApiViewV2


urlpatterns = patterns(
    '',
    url('^(?P<grant_type>(access_token|refresh_token))/$',
        csrf_exempt(AccessTokenView.as_view()),
        name='oauth2_access_token'),

    url('^login/$', TokenLoginOpenApiView.as_view(),
        name='oauth2_token_login'),

    url('^login/v2/$', TokenLoginOpenApiViewV2.as_view(),
        name='oauth2_token_login_v2'),
)
