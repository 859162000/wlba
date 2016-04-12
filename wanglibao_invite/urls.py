# encoding:utf-8
from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns(
    '',
    url(r'^ser_redpacket_index/$', TemplateView.as_view(template_name="service_redpacket_index.jade")),
    url(r'^ser_redpacket_get/$', TemplateView.as_view(template_name="service_redpacket_get.jade")),
    url(r'^ser_redpacket_code/$', TemplateView.as_view(template_name="service_redpacket_code.jade")),
    url(r'^ser_redpacket_set/$', TemplateView.as_view(template_name="service_redpacket_set.jade")),
    url(r'^ser_redpacket_bind/$', TemplateView.as_view(template_name="service_redpacket_bind.jade")),

)



