# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt
from .views import AccessTokenView


urlpatterns = patterns(
    '',
    url('^(?P<grant_type>(access_token|refresh_token))/?$',
        csrf_exempt(AccessTokenView.as_view()),
        name='access_token'),
)
