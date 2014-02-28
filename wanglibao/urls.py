from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import login
from django.views.generic import TemplateView
from trust.views import TrustHomeView, TrustProductsView, TrustDetailView
from wanglibao.forms import EmailOrPhoneAuthenticationForm
from wanglibao.views import RegisterView
from wanglibao_bank_financing.views import FinancingHomeView, FinancingProductsView
from wanglibao_fund.views import FundHomeView
from wanglibao_portfolio.views import PortfolioHomeView

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name="index.jade"), name="index"),

    url(r'^portfolio/', PortfolioHomeView.as_view(), name="portfolio_home"),

    url(r'^trust/home/', TrustHomeView.as_view(), name="trust_home"),
    url(r'^trust/products/', TrustProductsView.as_view(), name="trust_product"),
    url(r'^trust/companies/', TemplateView.as_view(template_name="trust_company.jade"), name="trust_company"),
    url(r'^trust/detail/(?P<id>\w+)', TrustDetailView.as_view(), name="trust_detail"),

    url(r'^financing/home/', FinancingHomeView.as_view(), name="financing_home"),
    url(r'^financing/products/', FinancingProductsView.as_view(), name="financing_products"),

    url(r'^fund/home/', FundHomeView.as_view(), name="fund_home"),
    url(r'^fund/products/', TemplateView.as_view(template_name="fund_products.jade"), name="fund_products"),

    url(r'^products/', TemplateView.as_view(template_name="products_search.jade"), name="products_search"),

    url(r'^api/', include('wanglibao_rest.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {
            "template_name": "html/login.html",
            "authentication_form": EmailOrPhoneAuthenticationForm,
        }),
    url(r'^accounts/register/$', RegisterView.as_view()),
    url(r'^accounts/activate/complete/$',
                           TemplateView.as_view(template_name='html/activation_complete.html'),
                           name='registration_activation_complete'),

    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
                            url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
                                {'document_root': settings.MEDIA_ROOT})
    )
