# encoding:utf-8
from django.conf.urls import patterns, url
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.decorators import login_required
import views


urlpatterns = patterns(
    '',
    #test
    url(r'^login/$', TemplateView.as_view(template_name="fuel_login.jade")),
    url(r'^(?P<e_type>\w+)/index/$', login_required(views.RevenueExchangeIndexView.as_view(), login_url='/fuel/login/'), name='index'),
    url(r'^buy/(?P<e_type>\w+)/(?P<p_id>\d+)/$', login_required(views.RevenueExchangeBuyView.as_view(), login_url='/fuel/login/'), name='fuel_buy'),
    url(r'^buy-record/(?P<e_type>\w+)/(?P<p_status>\w+)/$', login_required(views.RevenueExchangeBuyRecordView.as_view(), login_url='/fuel/login/'), name='fuel_buy_record'),
    url(r'^exchange-record/(?P<e_type>\w+)/(?P<p_status>\w+)/$', login_required(views.RevenueExchangeRecordView.as_view(), login_url='/fuel/login/'), name='fuel_exchange_record'),
    url(r'^statistics/(?P<e_type>\w+)/$', login_required(views.RevenueExchangeStatisticsView.as_view(), login_url='/fuel/login/'), name='fuel_statistics'),

    url(r'^recharge/$', TemplateView.as_view(template_name="fuel_recharge.jade")),
    url(r'^account/$', TemplateView.as_view(template_name="fuel_account.jade")),
    url(r'^change/login-psw/$', TemplateView.as_view(template_name="fuel_changePSW.jade")),
    url(r'^change/trans-psw/$', TemplateView.as_view(template_name="fuel_change_transactionPSW.jade")),
    url(r'^set/trans-psw/$', TemplateView.as_view(template_name="fuel_set_transactionPSW.jade")),
    url(r'^authentication/$', TemplateView.as_view(template_name="fuel_authentication.jade")),
    url(r'^about/$', TemplateView.as_view(template_name="fuel_about.jade")),
    url(r'^bank/$', TemplateView.as_view(template_name="fuel_bank.jade")),
    url(r'^set/bank/$', TemplateView.as_view(template_name="fuel_set_bank.jade")),

    url(r'^records/product/$', TemplateView.as_view(template_name="fuel_records_audit.jade")),
    url(r'^records/exchange/$', TemplateView.as_view(template_name="fuel_records_exchange.jade")),
    url(r'^statistic/$', TemplateView.as_view(template_name="fuel_statistics.jade")),
    url(r'^regist/$', TemplateView.as_view(template_name="fuel_regist.jade")),
    url(r'^regist/authentication/', TemplateView.as_view(template_name="fuel_regist_authentication.jade")),
    url(r'^regist/bank/', TemplateView.as_view(template_name="fuel_regist_bank.jade")),
    url(r'^regist/end/', TemplateView.as_view(template_name="fuel_regist_end.jade")),
    url(r'^activity/', TemplateView.as_view(template_name="fuel_activity.jade")),
    url(r'^dec/', TemplateView.as_view(template_name="fuel_product_dec.jade")),

)
