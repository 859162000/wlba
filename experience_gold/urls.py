# encoding: utf-8

from django.conf.urls import patterns, url

from experience_gold.backends import ExperienceBuyView

urlpatterns = patterns(
    '',
    url(r'^buy/$', ExperienceBuyView.as_view()),
)

