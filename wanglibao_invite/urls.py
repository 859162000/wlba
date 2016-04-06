# encoding:utf-8
from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns(
    '',
    url(r'^ser_redpack_index/$', TemplateView.as_view(template_name="service_redpack_index.jade")),

)



