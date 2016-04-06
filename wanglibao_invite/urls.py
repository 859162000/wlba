# encoding:utf-8
from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns(
    '',
    url(r'^sub_checkIn_share/$', TemplateView.as_view(template_name="service_checkIn_share.jade")),

)



