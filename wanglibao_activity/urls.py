# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from wanglibao_activity.views import TemplatesFormatTemplate, PcActivityShowHomeView


urlpatterns = patterns(
    '',
    url(r'zero/(?P<id>\d+)/$', TemplatesFormatTemplate.as_view(template_name='template_zero.jade')),
    url(r'^top/$', TemplateView.as_view(template_name="top.jade")),

    #url(r'^area/$', TemplateView.as_view(template_name="area.jade")),
    url(r'^area/', PcActivityShowHomeView.as_view(), name="area"),
)
