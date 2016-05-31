# -*- coding: utf-8 -*-

from adminplus.sites import AdminSitePlus
from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf import settings
# from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, RedirectView
from wanglibao.views import IndexView, SecurityView, PartnerView
from wanglibao_account.cooperation import CoopQuery, CsaiUserQuery, CsaiInvestmentQuery, ZhongniuP2PQuery, \
    ZhongniuP2PDataQuery, CoopInvestmentQuery, ZOP2PListView, ZORecordView, ZOCountView, MidaiSuccessView, MidaiNewView, \
    Rong360P2PListView, Rong360TokenView, XiguaP2PListView, XiguaP2PQueryView
from wanglibao_margin.php_api import GetUserInfo, GetMarginInfo, SendInsideMessage, CheckTradePassword, YueLiBaoBuy, \
    YueLiBaoCheck, YueLiBaoCancel, YueLiBaoRefund, AssignmentOfClaimsBuy, SendMessages, YueLiBaoBuyFail, \
    AssignmentBuyFail, GetUnreadMgsNum, YueLiBaoBuyStatus, AssignmentBuyStatus, GetUserUnreadMgsNum, GetRedPacks, \
    SendRedPacks, GetAPPUser, CheckAppTradePassword, GetAjaxRedPacks, GetIOSRedPacks
from wanglibao_pay.views import AdminTransactionWithdraw, AdminTransactionP2P, AdminTransactionDeposit
from wanglibao_p2p.views import AdminP2PUserRecord
from wanglibao_banner.views import (HiringView, AboutView, CompanyView, TeamView, MilestoneView,
                                    ResponsibilityView, ContactView, AgreementView, DirectorateView,
                                    AgreementAutoView, DynamicHomeView, DynamicDetailView)

from marketing.cooperationapi import HeXunListAPI, WangDaiListAPI, WangDaiByDateAPI, WangdaiEyeListAPIView, \
    WangdaiEyeEquityAPIView, XunleiP2PListAPIView, XunleiP2PbyUser, DuoZhuanByDateAPI
from marketing.views import NewsListView, NewsDetailView, AppShareViewShort, ShortAppShareRegView,\
    AppShareViewSuccess, AppShareViewError, RockFinanceQRCodeView
from wanglibao.views import landpage_view
from wanglibao_sms.views import ArriveRate

admin.site = AdminSitePlus()
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', IndexView.as_view(), name="index"),
    url(r'^security/', SecurityView.as_view(), name="security"),
    url(r'^pc_guide/', TemplateView.as_view(template_name="pc_guide.jade")),
    url(r'^favicon.ico', RedirectView.as_view(url="/static/favicon.ico")),

    # url(r'^portfolio/', PortfolioHomeView.as_view(), name="portfolio_home"),

    # url(r'^trust/', include('trust.urls')),
    # url(r'^financing/home/', FinancingHomeView.as_view(), name="financing_home"),
    # url(r'^financing/products/', FinancingProductsView.as_view(), name="financing_products"),
    # url(r'^financing/detail/(?P<id>\w+)', FinancingDetailView.as_view(), name="financing_detail"),

    # Comment by hb on 2016-04-25
    #url(r'^fund/products/', FundProductsView.as_view(), name="fund_home"),
    #url(r'^fund/detail/(?P<id>\w+)', FundDetailView.as_view(), name="fund_detail"),

    # Comment by hb on 2016-04-25
    #url(r'^cash/products/', CashHomeView.as_view(), name="cash_home"),
    #url(r'^cash/detail/(?P<id>\w+)', CashDetailView.as_view(), name="cash_detail"),

    url(r'^p2p/', include('wanglibao_p2p.urls')),

    url(r'^products/', TemplateView.as_view(template_name="products_search.jade"), name="products_search"),

    # url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^api/', include('wanglibao_rest.urls')),
    url(r'^help/', include('wanglibao_help.urls')),
    url(r'^mobile/', include('wanglibao_mobile.urls')),
    url(r'^' + settings.ADMIN_ADDRESS + '/', include('weixin.admin_urls')),
    url(r'^' + settings.ADMIN_ADDRESS + '/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
    url(r'^accounts/', include('wanglibao_account.urls')),
    # url(r'^shumi/', include('shumi_backend.urls')),
    url(r'^pay/', include('wanglibao_pay.urls')),
    url(r'^app/', include('wanglibao_app.urls')),

    # url(r'^howto/', TemplateView.as_view(template_name="howto.jade")),
    url(r'^hiring/', HiringView.as_view(), name="hiring"),
    url(r'^dynamic/$', DynamicHomeView.as_view(), name="dynamic"),
    url(r'^dynamic/detail/(?P<id>\d+)/$', DynamicDetailView.as_view(), name="dynamic_detail"),
    url(r'^about/', AboutView.as_view(), name='about'),
    url(r'^company/', CompanyView.as_view(), name="company"),
    url(r'^team/', TeamView.as_view(), name="team"),
    url(r'^partner/', PartnerView.as_view(), name="partner"),
    url(r'^milestone/', MilestoneView.as_view(), name="milestone"),
    url(r'^responsibility/', ResponsibilityView.as_view(), name="responsibility"),
    url(r'^contact_us/', ContactView.as_view(), name="contact_us"),
    # url(r'^directorate/', DirectorateView.as_view(), name="directorate"),
    url(r'^news/list', NewsListView.as_view(), name="news_list"),
    url(r'^news/detail/(?P<id>\d+)', NewsDetailView.as_view(), name="news_detail"),
    # url(r'^newbie/', TemplateView.as_view(template_name="newbie.jade")),
    # url(r'^why_portfolio/', TemplateView.as_view(template_name="why_portfolio.jade")),
    url(r'^agreement/', AgreementView.as_view(), name="agreement"),
    url(r'^mobile/agreement/', TemplateView.as_view(template_name="mobile_agreement.jade")),
    url(r'^mobile/about/', TemplateView.as_view(template_name="mobile_about.jade")),
    url(r'^ckeditor/', include('ckeditor.urls')),

    url(r'^preorder/', include('wanglibao_preorder.urls')),
    url(r'^activity/', include('marketing.urls')),
    # url(r'^activity/', include('marketing.urls')),
    url(r'^announcement/', include('wanglibao_announcement.urls')),
    url(r'^redpacket/', include('wanglibao_redpack.urls')),
    url(r'^templates/', include('wanglibao_activity.urls')),
    url(r'^taojin/', RedirectView.as_view(url="/activity/pan_gold/")),

    url(r'^tender_agreement/',  AgreementAutoView.as_view(), name="agreement_auto"),
    url(r'^lottery/', include('wanglibao_lottery.urls')),
    url(r'^landpage/', landpage_view),

    url(r'^finance', TemplateView.as_view(template_name="financing.jade")),
    url(r'^data_cube', TemplateView.as_view(template_name="data_cube.jade")),
    url(r'^generalize', TemplateView.as_view(template_name="client_generalize.jade")),
    url(r'^qiye/', include('wanglibao_qiye.urls')),
)

urlpatterns += patterns(
    '',
    url(r'^captcha/', include('captcha.urls')),
    url(r'^media/(?P<path>.*)$', 'file_storage.views.serve'),
)

#add by Yihen@20150813,反作弊的相关接口处理在此
urlpatterns += patterns(
    '',
    url(r'^anti/', include('wanglibao_anti.urls')),
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
    #多赚
    url(r'^getWanglibaoData/$', DuoZhuanByDateAPI.as_view()),
    # 和讯网
    url(r'^hexun/p2plist.json', HeXunListAPI.as_view()),
    # 网贷天眼
    url(r'^api/loans/$', WangdaiEyeListAPIView.as_view()),
    url(r'^api/data/$', WangdaiEyeEquityAPIView.as_view()),
    # 迅雷
    url(r'^api/xunlei/getProjectList/$', XunleiP2PListAPIView.as_view()),
    url(r'^api/xunlei/getXLUserInvestInfo/$', XunleiP2PbyUser.as_view()),
    # # 天芒云
    # url(r'^api/tmyun/getRegisterList/(?P<startday>.*)/(?P<endday>.*)/$', TianmangRegisterQuery.as_view()),
    # url(r'^api/tmyun/getIDVerificationList/(?P<startday>.*)/(?P<endday>.*)/$', TianmangIDVerificationQuery.as_view()),
    # url(r'^api/tmyun/getInvestList/(?P<startday>.*)/(?P<endday>.*)/$', TianmangInvestQuery.as_view()),
    # url(r'^api/tmyun/getInvestListNotConfirm/(?P<startday>.*)/(?P<endday>.*)/$', TianmangInvestNotConfirmQuery.as_view()),
    # url(r'^api/tmyun/getCardBindList/(?P<startday>.*)/(?P<endday>.*)/$', TianmangCardBindQuery.as_view()),
    # # 易瑞特
    # url(r'^api/yiruite/getInfoList/(?P<startday>.*)/(?P<endday>.*)/(?P<sign>.*)/$', YiruiteQuery.as_view()),
    # # 蹦蹦网
    # url(r'^api/bengbeng/getInfoList/(?P<startday>.*)/(?P<endday>.*)/(?P<sign>.*)/$', BengbengQuery.as_view())
    url(r'^api/coopinfo/(?P<channel_code>[a-z0-9A-Z_]*)/(?P<user_type>[a-z0-9A-Z_]*)/(?P<start_day>[0-9]*)/(?P<end_day>[0-9]*)/(?P<sign>[a-z0-9A-Z_]*)/$', CoopQuery.as_view()),
    url(r'^api/coopinfo/(?P<channel_code>[a-z0-9A-Z_]*)/(?P<user_type>[a-z0-9A-Z_]*)/(?P<start_day>[0-9]*)/(?P<end_day>[0-9]*)/(?P<sign>[a-z0-9A-Z_]*)/(?P<page>[0-9]*)/$', CoopQuery.as_view()),
    url(r'^api/coopinvestinfo/(?P<channel_code>[a-z0-9A-Z_]*)/(?P<p_id>[0-9]*)/(?P<sign>[a-z0-9A-Z_]*)/$', CoopInvestmentQuery.as_view()),

    url(r'^api/csai/users/', CsaiUserQuery.as_view()),
    url(r'^api/csai/investment/', CsaiInvestmentQuery.as_view()),

    url(r'^api/zhongniu/products/', ZhongniuP2PQuery.as_view()),
    url(r'^api/zhongniu/getData/$', ZhongniuP2PDataQuery.as_view()),

    url(r'^api/01/p2plist/$', ZOP2PListView.as_view()),
    url(r'^api/01/record/$', ZORecordView.as_view()),
    url(r'^api/01/count/$', ZOCountView.as_view()),

    url(r'^api/rong360/token/$', Rong360TokenView.as_view()),
    url(r'^api/rong360/list/$', Rong360P2PListView.as_view()),

    url(r'^api/loans/success/$', MidaiSuccessView.as_view()),
    url(r'^api/loans/new/$', MidaiNewView.as_view()),

    # 西瓜理财
    url(r'^api/xglcApi/onSaleProduct/$', XiguaP2PListView.as_view()),
    url(r'^api/xglcApi/productStateInfo/$', XiguaP2PQueryView.as_view()),

    url(r'^AK7WtEQ4Q9KPs8Io_zOncw/wanglibao_sms/arrive_rate/$', ArriveRate.as_view(), name='arrive_rate'),

    #url(r'^ws/$', ShortAppShareRegView.as_view(), name="app_share_reg_short"),
    url(r'^aws/$', AppShareViewShort.as_view(), name="app_invite"),
    url(r'^wst/(?P<phone>\w+)', AppShareViewSuccess.as_view(), name="app_invite_success"),
    url(r'^wsf/(?P<phone>\w+)', AppShareViewError.as_view(), name="app_invite_error"),
    url(r'^app-invite-server/$', TemplateView.as_view(template_name="app_invite_server.jade")),

    url(r'^rock/finance/qrcode/$', RockFinanceQRCodeView.as_view(), name="qrcode"),

    # urls for php api by zhoudong
    url(r'^php/get_user/$', GetUserInfo.as_view(), name='php_user_info'),
    # url(r'^php/margin/$', GetMarginInfo.as_view(), name='php_margin_info'),
    # 单条站内信
    url(r'^php/send_message/inside/$', SendInsideMessage.as_view(), name='php_send_inside_message'),
    url(r'^php/unread_messages/$', GetUnreadMgsNum.as_view(), name='php_unread_messages'),
    url(r'^api/php/unread_messages/$', GetUserUnreadMgsNum.as_view(), name='php_self_unread_messages'),
    # 发送短信, 是否是营销类传参数 ext 分开.
    url(r'^php/send_messages/$', SendMessages.as_view(), name='php_send_messages'),

    url(r'^php/trade_password/$', CheckTradePassword.as_view(), name='php_trade_password'),
    url(r'^php/app/trade_password/$', CheckAppTradePassword.as_view(), name='php_app_trade_password'),
    url(r'^php/redpacks/list/$', GetRedPacks.as_view(), name='php_unused_redpacks'),
    url(r'^php/redpacks/list/ios/$', GetIOSRedPacks.as_view(), name='php_unused_redpacks'),
    url(r'^php/redpacks/ajax/list/$', GetAjaxRedPacks.as_view(), name='php_unused_redpacks_ajax'),

    url(r'^php/yue/buy/$', YueLiBaoBuy.as_view(), name='php_buy_yuelibao'),
    url(r'^php/yue/fail/$', YueLiBaoBuyFail.as_view(), name='php_buy_yuelibao_fail'),
    url(r'^php/yue/status/$', YueLiBaoBuyStatus.as_view(), name='php_buy_yuelibao_status'),
    url(r'^php/yue/check/$', YueLiBaoCheck.as_view(), name='php_check_yuelibao'),
    url(r'^php/yue/cancel/$', YueLiBaoCancel.as_view(), name='php_cancel_yuelibao'),
    url(r'^php/yue/refund/$', YueLiBaoRefund.as_view(), name='php_refund_yuelibao'),

    url(r'^php/assignment/buy/$', AssignmentOfClaimsBuy.as_view(), name='php_buy_assignment'),
    url(r'^php/assignment/status/$', AssignmentBuyStatus.as_view(), name='php_buy_assignment_status'),
    url(r'^php/assignment/fail/$', AssignmentBuyFail.as_view(), name='php_buy_assignment_fail'),
    url(r'^php/redpacks/send/$', SendRedPacks.as_view(), name='send_redpacks_by_push'),

    url(r'^php/app/user/get/$', GetAPPUser.as_view(), name='get_app_user'),

    # url(r'^php/logout/$', logout_with_cookie, name='php_logout_cookie'),
)

# 短信
urlpatterns += patterns(
    '',
    url(r'wanglibao_sms/', include('wanglibao_sms.urls'))
)

# 微信
urlpatterns += patterns(
    '',
    url(r'weixin/', include('weixin.urls')),
    url(r'weixin_activity/', include('wanglibao_reward.urls')),
)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )

handler404 = 'wanglibao.views.page_not_found'
handler500 = 'wanglibao.views.server_error'

# 网站地图
from django.contrib.sitemaps import GenericSitemap, Sitemap
from wanglibao_p2p.models import P2PProduct
from wanglibao_announcement.models import Announcement

p2p_product_dict = {
    'queryset': P2PProduct.objects.order_by('-end_time').all(),
    'date_field': 'end_time',
}

announcement_dict = {
    'queryset': Announcement.objects.all(),
    'date_field': 'updatetime'
}


class StaticViewSitemap(Sitemap):
    priority = 0.7
    changefreq = 'daily'

    def items(self):
        return [
            (u'首页', '/'),
            (u'理财专区', '/p2p/list/'),
            (u'基金', '/fund/products/'),
            (u'安全保障', '/security/'),
            (u'帮助中心', '/help/'),
            (u'媒体报道', '/news/list/'),
            (u'关于我们', '/about/'),
            (u'管理团队', '/team/'),
            (u'公司展示', '/company/'),
            (u'战略合作伙伴', '/partner/'),
            (u'网利宝大事记', '/milestone/'),
            (u'企业社会责任', '/responsibility/'),
            (u'网站公告', '/announcement/'),
            (u'招贤纳士', '/hiring/'),
            (u'联系方式', '/contact_us/'),
        ]

    def location(self, item):
        return item[1]

    def lastmod(self, item):
        import datetime
        return datetime.datetime.now()


sitemaps = {
    'all': StaticViewSitemap,
    'p2p-products': GenericSitemap(p2p_product_dict, priority=0.8),
    'announcements': GenericSitemap(announcement_dict, priority=0.6)
}

urlpatterns += patterns(
    'django.contrib.sitemaps.views',
    (r'^sitemap\.xml$', 'index', {'sitemaps': sitemaps}),
    (r'^sitemap-(?P<section>.+)\.xml$', 'sitemap', {'sitemaps': sitemaps}),
)

