# encoding:utf-8
from django.conf.urls import patterns, url
from django.views.generic import TemplateView, RedirectView
import views

urlpatterns = patterns(
    '',
    url(r'^connect/(?P<id>\w+)/', views.ConnectView.as_view()),
    url(r'^list/$', TemplateView.as_view(template_name="weixin_list.jade")),
)
