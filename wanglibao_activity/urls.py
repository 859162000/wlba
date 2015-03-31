# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from wanglibao_activity.views import TemplatesFormatTemplate


urlpatterns = patterns(
    '',
    url(r'activity/(?P<id>\w+)', TemplatesFormatTemplate.as_view(template_name='lx.jade')),
)
