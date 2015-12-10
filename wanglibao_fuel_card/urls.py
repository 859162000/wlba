# encoding:utf-8
from django.conf.urls import patterns, url
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.decorators import login_required
import views

urlpatterns = patterns(
    '',
    #test
    url(r'^index/$', TemplateView.as_view(template_name="fuel_index.jade")),
    url(r'^buy/$', TemplateView.as_view(template_name="fuel_buy.jade")),
    url(r'^recharge/$', TemplateView.as_view(template_name="fuel_recharge.jade")),
    url(r'^account/$', TemplateView.as_view(template_name="fuel_account.jade")),

)
