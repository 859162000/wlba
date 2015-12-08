# encoding: utf-8

from django.views.generic import TemplateView
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from experience_gold.backends import ExperienceBuyAPIView, GetExperienceAPIView
from experience_gold.views import ExperienceGoldView

urlpatterns = patterns(
    '',
    url(r'^buy/$', ExperienceBuyAPIView.as_view()),
    url(r'^get_experience/$', GetExperienceAPIView.as_view()),
    url(r'^experience/(?P<template>(account|redirect))/$',
        login_required(ExperienceGoldView.as_view(),
                       login_url='/accounts/token_login/'), name="experience_token_login"
        ),
    url(r'^experience/(?P<template>(mobile|gold))/$', ExperienceGoldView.as_view(), name="experience_gold"),
)

