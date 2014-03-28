from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from trust.views import TrustHomeView, TrustProductsView, TrustDetailView
from wanglibao.forms import EmailOrPhoneAuthenticationForm
from wanglibao.views import RegisterView, IndexView, AccountSettingView, PasswordResetGetIdentifierView, ResetPassword
from wanglibao_bank_financing.views import FinancingHomeView, FinancingProductsView, FinancingDetailView
from wanglibao_cash.views import CashHomeView, CashDetailView
from wanglibao_fund.views import FundHomeView, FundDetailView
from wanglibao_portfolio.views import PortfolioHomeView

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', IndexView.as_view(), name="index"),

    url(r'^portfolio/', PortfolioHomeView.as_view(), name="portfolio_home"),

    url(r'^trust/home/', TrustHomeView.as_view(), name="trust_home"),
    url(r'^trust/products/', TrustProductsView.as_view(), name="trust_product"),
    url(r'^trust/companies/', TemplateView.as_view(template_name="trust_company.jade"), name="trust_company"),
    url(r'^trust/detail/(?P<id>\w+)', TrustDetailView.as_view(), name="trust_detail"),

    url(r'^financing/home/', FinancingHomeView.as_view(), name="financing_home"),
    url(r'^financing/products/', FinancingProductsView.as_view(), name="financing_products"),
    url(r'^financing/detail/(?P<id>\w+)', FinancingDetailView.as_view(), name="financing_detail"),

    url(r'^fund/home/', FundHomeView.as_view(), name="fund_home"),
    url(r'^fund/products/', TemplateView.as_view(template_name="fund_products.jade"), name="fund_products"),
    url(r'^fund/detail/(?P<id>\w+)', FundDetailView.as_view(), name="fund_detail"),

    url(r'^cash/home/', CashHomeView.as_view(), name="cash_home"),
    url(r'^cash/products/', TemplateView.as_view(template_name="cash_products.jade"), name="cash_products"),
    url(r'^cash/detail/(?P<id>\w+)', CashDetailView.as_view(), name="cash_detail"),

    url(r'^products/', TemplateView.as_view(template_name="products_search.jade"), name="products_search"),

    url(r'^api/', include('wanglibao_rest.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {
            "template_name": "html/login.html",
            "authentication_form": EmailOrPhoneAuthenticationForm,
        }, name="login"),
    url(r'^accounts/register/$', RegisterView.as_view()),
    url(r'^accounts/password/change/$', "wanglibao.views.password_change", name='password_change'),
    url(r'^accounts/password/change/done/$', TemplateView.as_view(template_name='html/password_change_done.html'),
        name='password_change_done'),
    url(r'^accounts/activate/complete/$',
        TemplateView.as_view(template_name='html/activation_complete.html'),
        name='registration_activation_complete'),
    url(r'^accounts/home/', TemplateView.as_view(template_name='account_home.jade')),
    url(r'^accounts/favorite/', TemplateView.as_view(template_name='account_favorite.jade')),
    url(r'^accounts/setting/', AccountSettingView.as_view(template_name='account_setting.jade')),
    url(r'^accounts/password/reset/identifier/', PasswordResetGetIdentifierView.as_view(), name="password_reset"),
    url(r'^accounts/password/reset/validate/', PasswordResetGetIdentifierView.as_view(), name="password_reset_validate"),
    url(r'^accounts/password/reset/send_mail/', "wanglibao.views.send_validation_mail", name="send_validation_mail"),
    url(r'^accounts/password/reset/send_validate_code/', "wanglibao.views.send_validation_phone_code", name="send_validation_phone_code"),
    url(r'^accounts/password/reset/validate_phone_code/', "wanglibao.views.validate_phone_code"),
    url(r'^accounts/password/reset/set_password/', ResetPassword.as_view(), name="password_reset_set_password"),
    url(r'^accounts/password/reset/done/', TemplateView.as_view(template_name="password_reset_done.jade"), name="password_reset_done"),
    url(r'^accounts/password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        {
            'post_reset_redirect': 'password_reset_done',
            'template_name': 'password_reset_confirm.jade',
        },
        name='auth_password_reset_confirm'),
    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
                            url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
                                {'document_root': settings.MEDIA_ROOT})
    )
