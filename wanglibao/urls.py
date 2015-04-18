# -*- coding: utf-8 -*-

from adminplus.sites import AdminSitePlus
from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView, RedirectView
from wanglibao.views import IndexView, SecurityView, PartnerView
from wanglibao_bank_financing.views import FinancingHomeView, FinancingProductsView, FinancingDetailView
from wanglibao_cash.views import CashHomeView, CashDetailView
from wanglibao_fund.views import FundDetailView, FundProductsView
from wanglibao_portfolio.views import PortfolioHomeView
from wanglibao_pay.views import AdminTransactionWithdraw, AdminTransactionP2P, AdminTransactionDeposit
from wanglibao_p2p.views import AdminP2PUserRecord
# from wanglibao_account.views import CjdaoApiView
from wanglibao_banner.views import HiringView, AboutView, CompanyView, TeamView, MilestoneView, \
    ResponsibilityView, ContactView, AgreementView

from marketing.cooperationapi import HeXunListAPI, WangDaiListAPI, WangDaiByDateAPI, WangdaiEyeListAPIView, \
    WangdaiEyeEquityAPIView, XunleiP2PListAPIView, XunleiP2PbyUser
from marketing.views import NewsListView, NewsDetailView
from wanglibao_activity.decorators import decorator_include
from wanglibao_activity.decorators import wap_activity_manage

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
    url(r'^help/', include('wanglibao_help.urls')),
    url(r'^' + settings.ADMIN_ADDRESS + '/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
    url(r'^accounts/', include('wanglibao_account.urls')),
    url(r'^shumi/', include('shumi_backend.urls')),
    url(r'^pay/', include('wanglibao_pay.urls')),

    # url(r'^howto/', TemplateView.as_view(template_name="howto.jade")),
    url(r'^hiring/', HiringView.as_view(), name="hiring"),
    url(r'^about/', AboutView.as_view(), name='about'),
    url(r'^company/', CompanyView.as_view(), name="company"),
    url(r'^team/', TeamView.as_view(), name="team"),
    url(r'^partner/', PartnerView.as_view(), name="partner"),
    url(r'^milestone/', MilestoneView.as_view(), name="milestone"),
    url(r'^responsibility/', ResponsibilityView.as_view(), name="responsibility"),
    url(r'^contact_us/', ContactView.as_view(),name="contact_us"),
    url(r'^news/list', NewsListView.as_view(), name="news_list"),
    url(r'^news/detail/(?P<id>\d+)', NewsDetailView.as_view(), name="news_detail"),
    # url(r'^newbie/', TemplateView.as_view(template_name="newbie.jade")),
    # url(r'^why_portfolio/', TemplateView.as_view(template_name="why_portfolio.jade")),
    url(r'^agreement/', AgreementView.as_view(), name="agreement"),
    url(r'^mobile/agreement/', TemplateView.as_view(template_name="mobile_agreement.jade")),
    url(r'^mobile/about/', TemplateView.as_view(template_name="mobile_about.jade")),
    url(r'^ckeditor/', include('ckeditor.urls')),

    url(r'^preorder/', include('wanglibao_preorder.urls')),
    url(r'^activity/', decorator_include(include('marketing.urls'), wap_activity_manage)),
    url(r'^announcement/', include('wanglibao_announcement.urls')),
    url(r'^redpacket/', include('wanglibao_redpack.urls')),
    url(r'^templates/', include('wanglibao_activity.urls')),
)

urlpatterns += patterns(
    '',
    url(r'^captcha/', include('captcha.urls')),
    url(r'^media/(?P<path>.*)$', 'file_storage.views.serve')
)


# the admin router about transaciton infdomation
urlpatterns += patterns(
    '',
    url(r'transaction/p2p', AdminTransactionP2P.as_view(), name='transaction_p2p'),
    url(r'transaction/deposit', AdminTransactionDeposit.as_view(), name='transaction_deposit'),
    url(r'transaction/withdraw', AdminTransactionWithdraw.as_view(), name='transaction_withdraw'),
    url(r'p2pequity/profile', AdminP2PUserRecord.as_view(), name='p2p_user_record'),
)

# the other Platform API
urlpatterns += patterns(
    '',
    # 网贷之家
    url(r'^tdt/getNowProjects.json', WangDaiListAPI.as_view()),
    url(r'^tdt/getProjectsByDate.json', WangDaiByDateAPI.as_view()),
    # 和讯网
    url(r'^hexun/p2plist.json', HeXunListAPI.as_view()),
    # 网贷天眼
    url(r'^api/loans/$', WangdaiEyeListAPIView.as_view()),
    url(r'^api/data/$', WangdaiEyeEquityAPIView.as_view()),
    # 迅雷
    url(r'^api/xunlei/getProjectList/$', XunleiP2PListAPIView.as_view()),
    url(r'^api/xunlei/getXLUserInvestInfo/$', XunleiP2PbyUser.as_view()),
    # 财经道
    # url(r'^accounts/cjdao/$', CjdaoApiView.as_view(), name='cjdao'),
)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )

handler404 = 'wanglibao.views.page_not_found'
handler500 = 'wanglibao.views.server_error'
