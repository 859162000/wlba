# encoding: utf-8

from django.views.generic import TemplateView
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from experience_gold.backends import ExperienceBuyAPIView, GetExperienceAPIView
from experience_gold.views import ExperienceGoldView, ExperienceAppDetailView, ExperienceDetailView

urlpatterns = patterns(
    '',
    url(r'^buy/$', ExperienceBuyAPIView.as_view()),
    url(r'^get_experience/$', GetExperienceAPIView.as_view()),
    url(r'^experience/(?P<template>(account|accounts))/$',
        login_required(ExperienceGoldView.as_view(),
                       login_url='/accounts/token_login/'), name="experience_token_login"
        ),
    url(r'^experience/account/nologin/$',
        login_required(ExperienceGoldView.as_view(),
                       login_url='/accounts/token_login/'), name="experience_token_nologin"
        ),
    url(r'^experience/(?P<template>(gold|redirect))/$', ExperienceGoldView.as_view(), name="experience_gold"),
    url(r'^experience/explain/$', TemplateView.as_view(template_name="experience_explain.jade")),
    url(r'^experience/detail/$', ExperienceDetailView.as_view(), name="experience_detail"),
    url(r'^experience/app_detail/$',
        login_required(ExperienceAppDetailView.as_view(),
                       login_url='/accounts/token_login/'), name="experience_app_detail"),
    url(r'^experience/mobile/$',
        login_required(ExperienceAppDetailView.as_view(),
                       login_url='/accounts/token_login/'), name="experience_mobile_detail"),
    # url(r'^experience/(?P<template>(account|accounts))/$', ExperienceGoldView.as_view()),
)

