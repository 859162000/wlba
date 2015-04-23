# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from wanglibao_activity.views import TemplatesFormatTemplate


urlpatterns = patterns(
    '',
    url(r'zero/(?P<id>\d+)/$', TemplatesFormatTemplate.as_view(template_name='template_zero.jade')),
)
