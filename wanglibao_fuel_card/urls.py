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
    url(r'^change/login-psw/$', TemplateView.as_view(template_name="fuel_changePSW.jade")),
    url(r'^change/trans-psw/$', TemplateView.as_view(template_name="fuel_change_transactionPSW.jade")),
    url(r'^set/trans-psw/$', TemplateView.as_view(template_name="fuel_set_transactionPSW.jade")),
    url(r'^authentication/$', TemplateView.as_view(template_name="fuel_authentication.jade")),
    url(r'^about/$', TemplateView.as_view(template_name="fuel_about.jade")),
    url(r'^bank/$', TemplateView.as_view(template_name="fuel_bank.jade")),

    url(r'^records/product/$', TemplateView.as_view(template_name="fuel_records_audit.jade")),
    url(r'^records/exchange/$', TemplateView.as_view(template_name="fuel_records_exchange.jade")),
    url(r'^statistic/$', TemplateView.as_view(template_name="fuel_statistics.jade")),
    url(r'^regist/$', TemplateView.as_view(template_name="fuel_regist.jade")),

)
