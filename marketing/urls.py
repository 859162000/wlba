from django.conf.urls import patterns, url
from django.views.generic import TemplateView, RedirectView
from marketing.views import AppShareView, AppShareRegView, NewYearView, AggregateView, IntroducedAwardTemplate, \
                            ThunderTenAcvitityTemplate, AppLotteryTemplate, OpenidPhoneForFencai
from play_list import Investment, InvestmentHistory, InvestmentRewardView
from django.contrib.auth.decorators import login_required
from wanglibao.views import BaiduFinanceView

urlpatterns = patterns(
    '',
    url(r'^wap/share/$', AppShareView.as_view(), name="app_share"),
    url(r'^wap/share_reg/$', AppShareRegView.as_view(), name="app_share_reg"),
    url(r'^share_reg_new/$', TemplateView.as_view(template_name="app_share_reg_new.jade")),
    url(r'^share_regnew_href/$', TemplateView.as_view(template_name="share_regnew_href.jade")),
    url(r'^wap/agreement/$', TemplateView.as_view(template_name="app_agreement.jade")),
    url(r'^full_send/$', TemplateView.as_view(template_name="full_send.jade")),
#    url(r'^ko_movie/$', TemplateView.as_view(template_name="ko_movie.jade")),
    url(r'^movie_login/$', TemplateView.as_view(template_name="app_movie_login.jade")),
    url(r'^agree_xieyi/$', TemplateView.as_view(template_name="agree_xieyi.jade")),
    url(r'^list_level/$', TemplateView.as_view(template_name="list_level.jade")),
    url(r'^father_day/$', TemplateView.as_view(template_name="father_day.jade")),
#    url(r'^newxunlei/$', TemplateView.as_view(template_name="newxunlei.jade")),
    url(r'^father/$', TemplateView.as_view(template_name="app_fatherday.jade")),
    url(r'^weipai/$', TemplateView.as_view(template_name="app_share_weipai.jade")),
    url(r'^pan_gold/$', TemplateView.as_view(template_name="pan_gold.jade")),
    url(r'^july_act/$', TemplateView.as_view(template_name="july_act.jade")),
    url(r'^act_invite/$', TemplateView.as_view(template_name="act_invite.jade")),
    url(r'^ganjiwang/$', TemplateView.as_view(template_name="ganjiwang.jade")),
    url(r'^baidu/$', TemplateView.as_view(template_name="baidu.jade"), name='marketing_baidu'),
#    url(r'^xunlei_august/$', TemplateView.as_view(template_name="xunlei-august.jade")),
    url(r'^singapore/$', TemplateView.as_view(template_name="singapore.jade")),
    url(r'^eight_gift/$', TemplateView.as_view(template_name="eight_gift.jade")),
    url(r'^advance/$', TemplateView.as_view(template_name="advance.jade")),
    url(r'^gold/$', TemplateView.as_view(template_name="gold.jade"), name='marketing_gold'),
    url(r'^qixi/$', TemplateView.as_view(template_name="qixi.jade")),
    # url(r'^xunlei_setp/$', TemplateView.as_view(template_name="xunlei_setp.jade"), name='marketing_xunlei_setp'),
    url(r'^xunlei_setp/$', ThunderTenAcvitityTemplate.as_view(template_name="xunlei_ten.jade")),
    url(r'^mid_autumn/$', TemplateView.as_view(template_name="mid-autumn.jade")),
    # url(r'^xunlei_ten/$', TemplateView.as_view(template_name="xunlei_ten.jade")),

    url(r'^anniversary/$', TemplateView.as_view(template_name="anniversary.jade")),
    url(r'^app_anniversary/$', TemplateView.as_view(template_name="app_anniversary.jade")),
    url(r'^eight_gift_two/$', TemplateView.as_view(template_name="eight_gift_two.jade")),
    url(r'^xingmei/$', TemplateView.as_view(template_name="xingmei.jade")),
    url(r'^pc_caipiao/$', TemplateView.as_view(template_name="pc_caipiao.jade")),
    #url(r'^september_activity/$', TemplateView.as_view(template_name="september_activity.jade")),
    url(r'^web-view/$', TemplateView.as_view(template_name="webView.html")),
    url(r'^web-center/$', TemplateView.as_view(template_name="fetchtoken.jade")),

    url(r'^android-view/$', TemplateView.as_view(template_name="android_view.html")),
    url(r'^new_user/$', TemplateView.as_view(template_name="new_user.jade")),
    url(r'^recommended/$', TemplateView.as_view(template_name="recommended.jade")),
    url(r'^national/$', TemplateView.as_view(template_name="national.jade")),
    url(r'^gold_two/$', TemplateView.as_view(template_name="gold_two.jade")),

    url(r'^baidu_finance/$', BaiduFinanceView.as_view(), name="baidu_finance"),
    url(r'^seckill/$', TemplateView.as_view(template_name="seckill.jade")),
    url(r'^november_new/$', TemplateView.as_view(template_name="november_new.jade")),
    url(r'^jucheng/$', TemplateView.as_view(template_name="jucheng.jade")),
    #url(r'^youku/$', TemplateView.as_view(template_name="youku_test.jade")),
    url(r'^two-eleven/$', TemplateView.as_view(template_name="two-eleven.jade")),
    url(r'^bid/$', TemplateView.as_view(template_name="bid.jade")),
    url(r'^365_gu/$', TemplateView.as_view(template_name="365_gu.jade")),
     url(r'thanksgiving/$', TemplateView.as_view(template_name="thanksgiving.jade")),
)

# app URL
urlpatterns += patterns(
    '',
    url(r'^app_father/$', TemplateView.as_view(template_name="app_fatherday.jade")),
    url(r'^app_movie/$', TemplateView.as_view(template_name="app_movie.jade")),
    url(r'^app_level/$', TemplateView.as_view(template_name="app_level.jade")),
    url(r'^app_invite/$', TemplateView.as_view(template_name="app_invite.jade")),
    url(r'^app_shareReward/$', TemplateView.as_view(template_name="app_gold_season.jade")),
    url(r'^app_request/$', TemplateView.as_view(template_name="app_request.jade")),
    url(r'^app_gold/$', TemplateView.as_view(template_name="app_gold_season.jade")),
    url(r'^app_july_act/$', TemplateView.as_view(template_name="app_july_act.jade")),
    url(r'^app_extension/$', TemplateView.as_view(template_name="app_extension.jade")),
#    url(r'^app_ele/$', TemplateView.as_view(template_name="app_ele.jade")),
    url(r'^app_eight_gift/$', TemplateView.as_view(template_name="app_eight_gift.jade")),
    url(r'^app_eight/$', TemplateView.as_view(template_name="app_eight.jade")),
    url(r'^xingmei/$', TemplateView.as_view(template_name="xingmei.jade")),
    url(r'^app_xingmei/$', TemplateView.as_view(template_name="app_xingmei.jade")),
    url(r'^h5_gold/$', TemplateView.as_view(template_name="h5_gold.jade")),
    url(r'^app_qixi/$', TemplateView.as_view(template_name="app_qixi.jade")),
    url(r'^app_gold_day/$', TemplateView.as_view(template_name="app_gold_day.jade")),
    url(r'^app_pc_download/$', TemplateView.as_view(template_name="app_pc_download.jade")),
    url(r'^app_lottery/$', AppLotteryTemplate.as_view(template_name="app_lottery.jade")),
    url(r'^lingcai/phone/$', OpenidPhoneForFencai.as_view()),
    url(r'^app_scratch/$', TemplateView.as_view(template_name="app_scratch.jade")),
    url(r'^app_scratch_copy/$', login_required(TemplateView.as_view(template_name="app_scratch_copy.jade"), login_url='/accounts/token_login/')),
    url(r'^app_scratch_copy/nologin/$', TemplateView.as_view(template_name="app_scratch_copy.jade")),
    url(r'^app_national/$', TemplateView.as_view(template_name="app_national.jade")),


    url(r'^app_eight_gift_two/$', TemplateView.as_view(template_name="app_eight_gift_two.jade")),
    url(r'^app_eight_gift_two_h5/$', TemplateView.as_view(template_name="app_eight_gift_two_h5.jade")),
    url(r'^wx_new_user/$', TemplateView.as_view(template_name="app_september.jade")),
    url(r'^app_new_user/$', TemplateView.as_view(template_name="app_september_h5.jade")),
    url(r'^channel_new_user/$', TemplateView.as_view(template_name="channel_new_user.jade")),
    url(r'^wx_anniversary/$', TemplateView.as_view(template_name="wx_anniversary.jade")),
    url(r'^app_anniversary/$', TemplateView.as_view(template_name="app_anniversary.jade")),
    url(r'^app_colorpage/$', TemplateView.as_view(template_name="app_colorpage.jade")),
    url(r'^app_fullpage/$', TemplateView.as_view(template_name="app_fullpage.jade")),
    url(r'^gold_season/$', TemplateView.as_view(template_name="gold_season.jade")),
    url(r'^share/index/$', TemplateView.as_view(template_name="share_index.jade")),
    url(r'^share/code/$', TemplateView.as_view(template_name="share_code.jade")),
    url(r'^share/old/$', TemplateView.as_view(template_name="share_old_user.jade")),
    url(r'^share/new/$', TemplateView.as_view(template_name="share_new_user.jade")),
    url(r'^app_wechatstart/$', TemplateView.as_view(template_name="app_weChatStart.jade")),
    url(r'^app_wechatdetail/$', TemplateView.as_view(template_name="app_weChatDetail.jade")),
    url(r'^app_wechatend/$', TemplateView.as_view(template_name="app_weChatEnd.jade")),
    url(r'^h5_mid_autumn/$', TemplateView.as_view(template_name="h5_mid_autumn.jade")),
    url(r'^app_mid_autumn/$', TemplateView.as_view(template_name="app_mid_autumn.jade")),
    url(r'^app_ten_year/$', TemplateView.as_view(template_name="app_ten_year.jade")),
    url(r'^app_recommended/$', TemplateView.as_view(template_name="app_recommended.jade")),
    url(r'^app_iPhone_6S/$', TemplateView.as_view(template_name="app_iPhone_6S.jade")),
    url(r'^app_gold_season/$', TemplateView.as_view(template_name="app_gold_season.jade")),
    url(r'^wx_gold_two/$', TemplateView.as_view(template_name="h5_gold_two.jade")),
    url(r'^app_gold_two/$', TemplateView.as_view(template_name="app_gold_two.jade")),
    url(r'^app_seckill/$', TemplateView.as_view(template_name="app_seckill.jade")),
    url(r'^app_halloween/$', TemplateView.as_view(template_name="app_halloween.jade")),

    url(r'^maimai_index/$', TemplateView.as_view(template_name="app_maimaiIndex.jade")),
    url(r'^maimai_rules/$', TemplateView.as_view(template_name="app_maimaiRule.jade")),
    url(r'^maimai_success/$', TemplateView.as_view(template_name="app_maimaiSuccess.jade")),
    url(r'^wechat_reward/$', TemplateView.as_view(template_name="app_wechatReward.jade")),
    url(r'^wechat_result/$', TemplateView.as_view(template_name="app_wechatReward_result.jade")),
    url(r'^wechat_rule/$', TemplateView.as_view(template_name="app_wechatReward_rule.jade")),

    url(r'^wx_november_new/$', TemplateView.as_view(template_name="h5_november_new.jade")),
    url(r'^app_xiaomei/$', TemplateView.as_view(template_name="app_xiaomei.jade")),
    url(r'^app_xiaomeier/$', TemplateView.as_view(template_name="app_xiaomeier.jade")),
    url(r'^wx_financing/$', TemplateView.as_view(template_name="h5_financing.jade")),

    url(r'^app_jucheng/$', TemplateView.as_view(template_name="app_jucheng.jade")),
    url(r'^app_two-eleven/$', TemplateView.as_view(template_name="app_two-eleven.jade")),
    url(r'^app_bid/$', TemplateView.as_view(template_name="app_bid.jade")),

    url(r'^app-invite/$', TemplateView.as_view(template_name="app_invite_friends.jade")),
    url(r'^app-invite-success/$', TemplateView.as_view(template_name="app_invite_success.jade")),
    url(r'^app-invite-error/$', TemplateView.as_view(template_name="app_invite_error.jade")),
)

urlpatterns += patterns(
    '',
    url(r'^aggregate/', AggregateView.as_view(template_name="aggregate.jade")),
)

urlpatterns += patterns(
    '',
    # url(r'^introduced_by/$', IntroducedAwardTemplate.as_view(template_name="introduced_by.jade")),
    url(r'^investment_reward/$', InvestmentRewardView.as_view(template_name="investment_reward.jade")),
    url(r'^investment/$', Investment.as_view(), name='day'),
)

#urlpatterns += patterns('',
#    url(r'^xunlei/july/$', TemplateView.as_view(template_name="xunlei_july.jade"), name='xunlei_july_activity')
#)
