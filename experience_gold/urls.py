# encoding: utf-8

from django.views.generic import TemplateView
from django.conf.urls import patterns, url

from experience_gold.backends import ExperienceBuyView
from experience_gold.views import ExperienceGoldView

urlpatterns = patterns(
    '',
    url(r'^buy/$', ExperienceBuyView.as_view()),
    url(r'^experience_account/$', TemplateView.as_view(template_name="account.jade")),
    url(r'^experience/(?P<template>\w+)/$', ExperienceGoldView.as_view(), name="experience_gold"),
)

