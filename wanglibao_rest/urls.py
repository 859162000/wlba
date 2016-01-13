#!/usr/bin/env python
# encoding:utf-8

from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from trust.views import TrustViewSet, IssuerViewSet
from wanglibao_account.views import (UserViewSet, ResetPasswordAPI, FundInfoAPIView,
                            AccountHomeAPIView, AccountP2PRecordAPI, AccountFundRecordAPI, AccountP2PAssetAPI,
                            AccountFundAssetAPI,
                            P2PAmortizationAPI, UserProductContract, ChangePasswordAPIView,
                            AddressAPIView, AddressListAPIView, AddressDeleteAPIView,
                            AddressGetAPIView, AccountInviteAPIView, MessageListAPIView,
                            MessageCountAPIView, MessageDetailAPIView,
                            AutomaticApiView, AccountInviteHikeAPIView,AccountInviteAllGoldAPIView,
                            AccountInviteIncomeAPIView, password_change,  PasswordCheckView)
from wanglibao_bank_financing.views import BankFinancingViewSet, BankViewSet
from wanglibao_banner.views import BannerViewSet
from wanglibao_buy.views import TradeInfoViewSet, DailyIncomeViewSet, TotalIncome
from wanglibao_cash.views import CashViewSet, CashIssuerViewSet
from wanglibao_favorite.views import FavoriteTrustViewSet, FavoriteFundViewSet, FavoriteFinancingViewSet, \
    FavoriteCashViewSet
from wanglibao_feedback.views import FeedbackViewSet
from wanglibao_fund.views import FundViewSet, FundIssuerViewSet
from wanglibao_hotlist.views import HotTrustViewSet, HotFundViewSet, MobileHotTrustViewSet, \
    MobileHotFundViewSet, MobileMainPageViewSet, MobileMainPageP2PViewSet
from wanglibao_p2p.views import PurchaseP2P, PurchaseP2PMobile, P2PProductViewSet, RecordView, \
    P2PProductDetailView, RepaymentAPIView
from wanglibao_pay.third_pay import  TheOneCardAPIView
from wanglibao_pay.views import (CardViewSet, BankCardAddView, BankCardListView, BankCardDelView, 
                            BankListAPIView, YeePayAppPayView, YeePayAppPayCallbackView,
                            YeePayAppPayCompleteView, WithdrawAPIView, FEEAPIView,
                            BindPayView, KuaiShortPayCallbackView, BindPayQueryView,
                            BindPayDelView, BindPayDynNumView, TradeRecordAPIView,
                            BindCardQueryView, UnbindCardView, BindPayDepositView, BindPayDynnumNewView,
                            BankCardDelNewView, BankListNewAPIView, YeeShortPayCallbackView)

from wanglibao_portfolio.views import PortfolioViewSet, ProductTypeViewSet
from wanglibao_preorder.views import PreOrderViewSet
from wanglibao_profile.views import ProfileView, TradePasswordView
from wanglibao_rest.views import (SendValidationCodeView, SendRegisterValidationCodeView,
                            UserExisting, RegisterAPIView, IdValidate, AdminIdValidate,
                            WeixinRegisterAPIView, IdValidateAPIView, ClientUpdateAPIView,
                            YTXVoiceCallbackAPIView, SendVoiceCodeAPIView, TestSendRegisterValidationCodeView,
                            SendVoiceCodeTwoAPIView, MobileDownloadAPIView, Statistics, KuaipanPurchaseListAPIView,
                            LatestDataAPIView, ShareUrlAPIView, TopsOfDayView, TopsOfWeekView, InvestRecord,
                            DepositGateAPIView, PushTestView, WeixinSendRegisterValidationCodeView,
                            GestureAddView, GestureUpdateView, GestureIsEnabledView, LoginAPIView, GuestCheckView,
                            CaptchaValidationCodeView, TopsOfEaringView, DistributeRedpackView, UserHasLoginAPI,
                            InnerSysSaveChannel, InnerSysSendSMS, InnerSysValidateID, DataCubeApiView, StatisticsInside,
                                  BidHasBindingForChannel)
from wanglibao_redpack.views import (RedPacketListAPIView, RedPacketChangeAPIView, RedPacketDeductAPIView,
                                     RedPacketSelectAPIView)

from marketing.play_list import InvestmentHistory
from marketing.views import (ActivityJoinLogAPIView, ActivityJoinLogCountAPIView, ThousandRedPackAPIView,
                             RockFinanceAPIView, RockFinanceForOldUserAPIView, RockFinanceCheckAPIView,
                             ThousandRedPackCountAPIView, ThunderActivityRewardCounter, QuickApplyerAPIView,
                             GiftOwnerInfoAPIView, RewardDistributeAPIView)
from weixin.views import P2PListWeixin
from wanglibao_account.views import ThirdOrderApiView, ThirdOrderQueryApiView
from marketing.views import UserActivityStatusAPIView
from wanglibao_reward.views import WeixinRedPackView, WeixinShareTools, DistributeRewardAPIView, XunleiActivityAPIView

router = DefaultRouter()

router.register(r'trusts', TrustViewSet)
router.register(r'issuers', IssuerViewSet)

router.register(r'bank_financings', BankFinancingViewSet)
router.register(r'banks', BankViewSet)

router.register(r'funds', FundViewSet)
router.register(r'fund_issuers', FundIssuerViewSet)

router.register(r'cashes', CashViewSet)
router.register(r'cash_issuers', CashIssuerViewSet)

router.register(r'portfolios', PortfolioViewSet)
router.register(r'products', ProductTypeViewSet)

router.register(r'hot_trusts', HotTrustViewSet)
router.register(r'hot_funds', HotFundViewSet)
router.register(r'mobile_hot_trusts', MobileHotTrustViewSet)
router.register(r'mobile_hot_funds', MobileHotFundViewSet)
router.register(r'mobile_main', MobileMainPageViewSet)
router.register(r'mobile_main_p2p', MobileMainPageP2PViewSet)

router.register(r'favorite/trusts', FavoriteTrustViewSet)
router.register(r'favorite/funds', FavoriteFundViewSet)
router.register(r'favorite/financings', FavoriteFinancingViewSet)
router.register(r'favorite/cashes', FavoriteCashViewSet)

router.register(r'p2ps', P2PProductViewSet)

router.register(r'pre_orders', PreOrderViewSet)
router.register(r'feedbacks', FeedbackViewSet)
router.register(r'trade_info', TradeInfoViewSet)
#router.register(r'banners', BannerViewSet)
# router.register(r'users', UserViewSet)

router.register(r'daily_income', DailyIncomeViewSet)

router.register(r'card', CardViewSet)

from django.views.decorators.csrf import csrf_exempt

urlpatterns = patterns(
    '',
    url(r'^banners/$', BannerViewSet.as_view()),
    url(r'^register/$', RegisterAPIView.as_view()),
    url(r'^register/wx/$', WeixinRegisterAPIView.as_view()),
    url(r'^change_password/$', ChangePasswordAPIView.as_view()),
    url(r'^reset_password/$', ResetPasswordAPI.as_view()),
    url(r'^check_password/$', PasswordCheckView.as_view()),
    url(r'captcha_validation/(?P<phone>\d{11})/$', CaptchaValidationCodeView.as_view()),
    url(r'^phone_validation_code/(?P<phone>\d{11})/$', SendValidationCodeView.as_view()),
    url(r'^phone_validation_code/register/(?P<phone>\d{11})/$', SendRegisterValidationCodeView.as_view()),
    url(r'^phone_validation_code/reset_password/(?P<phone>\d{11})/$', SendValidationCodeView.as_view()),

    url(r'^weixin/phone_validation_code/register/(?P<phone>\d{11})/$', WeixinSendRegisterValidationCodeView.as_view()),

    url(r'^test/register/(?P<phone>\d{11})/$', TestSendRegisterValidationCodeView.as_view()),

    url(r'^user_login/$', UserHasLoginAPI.as_view()),
    url(r'^user_exists/(?P<identifier>[\w\.@]+)/$', UserExisting.as_view()),
    url(r'^profile/', ProfileView.as_view()),
    url(r'^total_income', TotalIncome.as_view()),
    url(r'^p2p/purchase/$', PurchaseP2P.as_view()),
    url(r'^p2p/purchase/mobile/$', PurchaseP2PMobile.as_view()),
    url(r'^p2ps/(?P<product_id>\d+)/records/', RecordView.as_view()),

    # url(r'^p2ps/$', P2PProductListView.as_view()),
    url(r'^p2ps/(?P<pk>[0-9]+)/$', P2PProductDetailView.as_view()),
    url(r'^p2ps/wx/', P2PListWeixin.as_view()),

    url(r'', include(router.urls)),
    #客户端使用,重写
    url(r'^id_validation/$', IdValidateAPIView.as_view()),
    url(r'^bank_card/add/$', BankCardAddView.as_view()),
    url(r'^bank_card/list/$', BankCardListView.as_view()),
    url(r'^bank_card/del/$', BankCardDelView.as_view()),
    url(r'^bank_card/del_new/$', BankCardDelNewView.as_view()),
    url(r'^bank/list/$', BankListAPIView.as_view()),
    url(r'^bank/list_new/$', BankListNewAPIView.as_view()),

    url(r'^id_validate/', IdValidate.as_view()),
    url(r'^admin_id_validate/$', AdminIdValidate.as_view()),

    url(r'^home/$', AccountHomeAPIView.as_view()),
    url(r'^home/p2precord', AccountP2PRecordAPI.as_view()),
    url(r'^home/fundrecord', AccountFundRecordAPI.as_view()),
    url(r'^home/p2passet', AccountP2PAssetAPI.as_view()),
    url(r'^home/fundasset', AccountFundAssetAPI.as_view()),
    url(r'^home/p2p/amortization/(?P<product_id>\d+)', P2PAmortizationAPI.as_view()),
    url(r'^home/invite/$', AccountInviteAPIView.as_view()),
    url(r'^home/automatic/$', AutomaticApiView.as_view()),
    url(r'^home/invite/hike/$', AccountInviteHikeAPIView.as_view()),
    url(r'^home/invite/broker/$', AccountInviteAllGoldAPIView.as_view()),
    url(r'^home/invite/income/$', AccountInviteIncomeAPIView.as_view()),
    url(r'^trade_record/', TradeRecordAPIView.as_view()),

    url(r'^p2p/contract/(?P<product_id>\d+)', UserProductContract.as_view()),
    url(r'^withdraw/$', WithdrawAPIView.as_view(), name="withdraw-api-view"),
    url(r'^fee/$', FEEAPIView.as_view(), name="withdraw-api-view"),

    url(r'^pay/gate/$', DepositGateAPIView.as_view(), name="pay-gate-api-view"),
    url(r'^pay/yee/app/deposit/$', YeePayAppPayView.as_view(), name="yee-deposit-view"),
    url(r'^pay/yee/app/deposit/callback/$', YeePayAppPayCallbackView.as_view(), name="yee-deposit-callback"),
    url(r'^pay/yee/app/deposit/complete/$', YeePayAppPayCompleteView.as_view(), name="yee-deposit-fcallback"),

    url(r'^pay/cnp/list/$', BindPayQueryView.as_view()),
    url(r'^pay/cnp/delete/$', BindPayDelView.as_view()),
    url(r'^pay/cnp/dynnum/$', BindPayDynNumView.as_view()),
    url(r'^pay/deposit/$', BindPayView.as_view(), name="kuai-deposit-view"),

    # 切换支付渠道重新
    url(r'^pay/cnp/list_new/$', BindCardQueryView.as_view()),
    url(r'^pay/cnp/delete_new/$', UnbindCardView.as_view()),
    url(r'^pay/cnp/dynnum_new/$', BindPayDynnumNewView.as_view(), name='dynnum-new'),
    url(r'^pay/deposit_new/$', BindPayDepositView.as_view(), name='deposit-new'),
    url(r'^pay/cnp/yee/callback/$', YeeShortPayCallbackView.as_view(), name="yee-deposit-callback"),

    #url(r'^pay/deposit/callback/$', KuaiPayCallbackView.as_view(), name="kuai-deposit-callback"),
    url(r'^pay/deposit/callback/$', csrf_exempt(KuaiShortPayCallbackView.as_view()), name="kuai-deposit-callback"),
    # 同卡进出
    url(r'^pay/the_one_card/$', TheOneCardAPIView.as_view()),


    url(r'^client_update/$', ClientUpdateAPIView.as_view()),
    url(r'^pushtest/$', PushTestView.as_view()),
    url(r'^ytx/voice_back', YTXVoiceCallbackAPIView.as_view()),
    url(r'^ytx/send_voice_code/$', SendVoiceCodeAPIView.as_view()),
    url(r'^ytx/send_voice_code/2/$', SendVoiceCodeTwoAPIView.as_view()),
    url(r'^marketing/tv/$', Statistics.as_view()),
    url(r'^marketing/tv_inside/$', StatisticsInside.as_view()),
    url(r'^p2p/investrecord', InvestRecord.as_view()),
    url(r'^mobiledownload/$', MobileDownloadAPIView.as_view()),
    url(r'^kuaipan/purchaselist/$', KuaipanPurchaseListAPIView.as_view()),
    url(r'^platform/latestdata/$', LatestDataAPIView.as_view()),
    url(r'^shareurl/$', ShareUrlAPIView.as_view()),
    url(r'^gettopofday/$', TopsOfDayView.as_view()),
    url(r'^gettopofweek/$', TopsOfWeekView.as_view()),
    url(r'^gettopofearings/', TopsOfEaringView.as_view()),

    url(r'^redpacket/$', RedPacketListAPIView.as_view()),
    url(r'^redpacket/exchange/$', RedPacketChangeAPIView.as_view()),
    url(r'^redpacket/deduct/$', RedPacketDeductAPIView.as_view()),
    url(r'^redpacket/selected/$', RedPacketSelectAPIView.as_view()),

    url(r'^message/count/$', MessageCountAPIView.as_view()),
    url(r'^message/(?P<message_id>\d+)/$', MessageDetailAPIView.as_view()), 
    url(r'^message/list/$', MessageListAPIView.as_view()),

    url(r'^address/$', AddressAPIView.as_view()),
    url(r'^address/list/$', AddressListAPIView.as_view()),
    url(r'^address/(?P<address_id>\d+)/$', AddressGetAPIView.as_view()),
    url(r'^address/delete/$', AddressDeleteAPIView.as_view()),

    url(r'^repayment/$', RepaymentAPIView.as_view()),  # 后台还款中标的接口

    url(r'^gesture/add/$', GestureAddView.as_view()),
    url(r'^gesture/update/$', GestureUpdateView.as_view()),
    url(r'^gesture/isenabled/$', GestureIsEnabledView.as_view()),
    url(r'^xunlei/8/check/$', GuestCheckView.as_view()),
    url(r'^trade_pwd/$', TradePasswordView.as_view()),
    url(r'^wechat/attention/(?P<phone>\d+)/$', WeixinRedPackView.as_view()),
    url(r'^distribute/redpack/(?P<phone>\d+)/$', DistributeRedpackView.as_view()),
    url(r'^inner/send_sms/$', InnerSysSendSMS.as_view()),
    url(r'^inner/validate_id/$', InnerSysValidateID.as_view()),
    url(r'^inner/save_channel/$', InnerSysSaveChannel.as_view()),
)

urlpatterns += patterns('',
    #url(r'^api-token-auth/', 'wanglibao_rest.views.obtain_auth_token'),
    url(r'^api-token-auth/', LoginAPIView.as_view()),
    url(r'wrapper/', 'drf_wrapper.views.wrapper_view'),
)

urlpatterns += patterns('',
    url(r'^fund_info/', FundInfoAPIView.as_view()),
)

urlpatterns += patterns('',
    url(r'^investment_history/', InvestmentHistory.as_view()),
)
urlpatterns += patterns(
    '',
    url(r'^xunlei/join/$', ActivityJoinLogAPIView.as_view()),
    url(r'^xunlei/join/count/$', ActivityJoinLogCountAPIView.as_view()),
    url(r'^thousand/redpack/$', ThousandRedPackAPIView.as_view()),
    url(r'^thousand/redpack/count/$', ThousandRedPackCountAPIView.as_view()),
    url(r'^xunlei/august/count/$', ThunderActivityRewardCounter.as_view()),
    url(r'^xunlei/award/action/$', 'marketing.views.ajax_xunlei'), #add by Yihen@20150821, 迅雷-网利宝 抽奖活动
    url(r'^xunlei/award/$', 'marketing.views.ajax_post'), #add by Yihen@20150821, 迅雷-网利宝 抽奖活动
    url(r'^xunlei/award/records/$', 'marketing.views.ajax_get_activity_record'), #add by Yihen@20150825, 迅雷-网利宝 抽奖活动记录
    url(r'^celebrate/awards/$', 'marketing.views.celebrate_ajax'), #add by Yihen@20150828, 网利宝一周年大转盘活动
    url(r'^award/common_september/$', 'marketing.views.september_award_ajax'), #add by Yihen@20150907,9月PC常规
    url(r'^quick/applyer/$', QuickApplyerAPIView.as_view()), #add by yihen@20151102 ,快速贷款人申请填写
    url(r'^gift/owner/$', GiftOwnerInfoAPIView.as_view()), #add by yihen@20151102 ,聚橙网领取门票接口
    url(r'^weixin/share/has_gift/$', WeixinShareTools.as_view()), #add by yihen@20151102 ,聚橙网领取门票接口
    url(r'^weixin/distribute/redpack/$', RewardDistributeAPIView.as_view()), #add by yihen@20151102 ,聚橙网领取门票接口
    url(r'^activity/reward/$', DistributeRewardAPIView.as_view()),
    #url(r'^rock/finance/$', RockFinanceAPIView.as_view()),  # 金融摇滚夜发送入场二维码 , 测试用，上线时去掉
    url(r'^check/qrcode/$', RockFinanceCheckAPIView.as_view(), name='rockfinance_checkresult'),  # 金融摇滚夜扫描接口
    url(r'^rock/finance/$', RockFinanceAPIView.as_view()),  # 金融摇滚夜投票的数据结果及获得入场二维码
    url(r'^rock/finance/old_user/$', RockFinanceForOldUserAPIView.as_view()),  # 金融摇滚夜投票的数据结果及获得入场二维码
    url(r'^xunlei/2016/1/$', XunleiActivityAPIView.as_view()),  # 迅雷1月接口
)


# app端改版新接口
urlpatterns += patterns(
    '',
    url(r'^m/', include('wanglibao_app.urls')),
)

# 第三方渠道业务接口
urlpatterns += patterns(
    '',
    url(r'^coop/order/receive/(?P<channel_code>[a-z0-9A-Z_]*)/$', ThirdOrderApiView.as_view()),
    url(r'^coop/order/query/$', ThirdOrderQueryApiView.as_view()),
)

# 用户活动状态查询接口
urlpatterns += patterns(
    '',
    url(r'^activity/joinInfo/$', UserActivityStatusAPIView.as_view()),
)

# 理财金接口
urlpatterns += patterns(
    '',
    url(r'^experience/', include('experience_gold.urls')),
)

# 数据魔方接口
urlpatterns += patterns(
    '',
    url(r'^datacube/$', DataCubeApiView.as_view()),
)

# 判断bid是否已经绑定渠道
urlpatterns += patterns(
    '',
    url(r'^has_binding/(?P<channel_code>[a-z0-9A-Z_]*)/(?P<bid>[a-z0-9A-Z_]*)/$', BidHasBindingForChannel.as_view()),
)
