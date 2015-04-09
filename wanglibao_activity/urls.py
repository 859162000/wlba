# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from wanglibao_activity.views import TemplatesFormatTemplate


urlpatterns = patterns(
    '',
    url(r'one/(?P<id>\w+)', TemplatesFormatTemplate.as_view(template_name='template_one.jade')),
    url(r'^index', TemplateView.as_view(template_name='tindex.jade')),
    url(r'iphone', TemplateView.as_view(template_name='iphone.jade')),

)
