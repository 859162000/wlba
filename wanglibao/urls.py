from adminplus.sites import AdminSitePlus
from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView, RedirectView
from wanglibao.views import IndexView, SecurityView
from wanglibao_bank_financing.views import FinancingHomeView, FinancingProductsView, FinancingDetailView
from wanglibao_cash.views import CashHomeView, CashDetailView
from wanglibao_fund.views import FundDetailView, FundProductsView
from wanglibao_portfolio.views import PortfolioHomeView
from wanglibao_pay.views import AdminTransactionWithdraw, AdminTransactionP2P, AdminTransactionDeposit


admin.site = AdminSitePlus()
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', IndexView.as_view(), name="index"),
    url(r'^security/', SecurityView.as_view(), name="security"),
    url(r'^favicon.ico', RedirectView.as_view(url="/static/favicon.ico")),

    url(r'^portfolio/', PortfolioHomeView.as_view(), name="portfolio_home"),

    url(r'^trust/', include('trust.urls')),
    url(r'^financing/home/', FinancingHomeView.as_view(), name="financing_home"),
    url(r'^financing/products/', FinancingProductsView.as_view(), name="financing_products"),
    url(r'^financing/detail/(?P<id>\w+)', FinancingDetailView.as_view(), name="financing_detail"),

    url(r'^fund/products/', FundProductsView.as_view(), name="fund_home"),
    url(r'^fund/detail/(?P<id>\w+)', FundDetailView.as_view(), name="fund_detail"),

    url(r'^cash/products/', CashHomeView.as_view(), name="cash_home"),
    url(r'^cash/detail/(?P<id>\w+)', CashDetailView.as_view(), name="cash_detail"),

    url(r'^p2p/', include('wanglibao_p2p.urls')),

    url(r'^products/', TemplateView.as_view(template_name="products_search.jade"), name="products_search"),

    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^api/', include('wanglibao_rest.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
    url(r'^accounts/', include('wanglibao_account.urls')),
    url(r'^shumi/', include('shumi_backend.urls')),
    url(r'^pay/', include('wanglibao_pay.urls')),

    #url(r'^howto/', TemplateView.as_view(template_name="howto.jade")),
    url(r'^hiring/', TemplateView.as_view(template_name="hiring.jade")),
    url(r'^about/', TemplateView.as_view(template_name="about.jade")),
    url(r'^team/', TemplateView.as_view(template_name="team.jade")),
    url(r'^partner/', TemplateView.as_view(template_name="partner.jade")),
    url(r'^milestone/', TemplateView.as_view(template_name="milestone.jade")),
    url(r'^responsibility/', TemplateView.as_view(template_name="responsibility.jade")),
    url(r'^contact_us/', TemplateView.as_view(template_name="contact_us.jade")),
    url(r'^news/', TemplateView.as_view(template_name="news.jade")),
    #url(r'^newbie/', TemplateView.as_view(template_name="newbie.jade")),
    #url(r'^why_portfolio/', TemplateView.as_view(template_name="why_portfolio.jade")),
    url(r'^agreement/', TemplateView.as_view(template_name="agreement.jade")),
    url(r'^mobile/agreement/', TemplateView.as_view(template_name="mobile_agreement.jade")),
    url(r'^mobile/about/', TemplateView.as_view(template_name="mobile_about.jade")),
    url(r'^ckeditor/', include('ckeditor.urls')),

    url(r'^preorder/', include('wanglibao_preorder.urls')),
    url(r'^activity/', include('marketing.urls')),
)

urlpatterns += patterns(
    '',
    url(r'^captcha/', include('captcha.urls')),
    url(r'^media/(?P<path>.*)$', 'file_storage.views.serve')
)


# the admin router about transaciton infomation
urlpatterns += patterns(
    '',
    url(r'transaction/p2p', AdminTransactionP2P.as_view(), name='transaction_p2p'),
    url(r'transaction/deposit', AdminTransactionDeposit.as_view(), name='transaction_deposit'),
    url(r'transaction/withdraw', AdminTransactionWithdraw.as_view(), name='transaction_withdraw'),
)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )

handler404 = 'wanglibao.views.page_not_found'
handler500 = 'wanglibao.views.server_error'
