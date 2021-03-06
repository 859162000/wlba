from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView, RedirectView
from marketing.views import AppShareView, AppShareRegView, NewYearView, AggregateView, IntroducedAwardTemplate, \
                            ThunderTenAcvitityTemplate, AppLotteryTemplate, OpenidPhoneForFencai, ThunderBindingApi, \
                            OpenHouseApiView, MaiMaiView, ShieldPlanView, ShieldPlanH5View, HMDP2PListView, \
                            SixBillionView, ThunderBindingQueryApi, CheFangDaiProductView, CheFangDaiProductAPPView
from play_list import Investment, InvestmentHistory, InvestmentRewardView
from django.contrib.auth.decorators import login_required
from wanglibao.views import BaiduFinanceView
from wanglibao_activity.views import PcActivityAreaView, ActivityAreaApi
from weixin.common.decorators import fwh_login_required

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
    # url(r'^xunlei_setp/$', ThunderTenAcvitityTemplate.as_view(template_name="xunlei_ten.jade"), name='xunlei_setp'),
    url(r'^mid_autumn/$', TemplateView.as_view(template_name="mid-autumn.jade")),
    # url(r'^xunlei_ten/$', TemplateView.as_view(template_name="xunlei_ten.jade")),

    url(r'^anniversary/$', TemplateView.as_view(template_name="anniversary.jade")),
    url(r'^app_anniversary/$', TemplateView.as_view(template_name="app_anniversary.jade")),
    url(r'^eight_gift_two/$', TemplateView.as_view(template_name="eight_gift_two.jade")),
    url(r'^xingmei/$', TemplateView.as_view(template_name="xingmei.jade")),
    url(r'^xingmei_two/$', TemplateView.as_view(template_name="xingmei_two.jade")),
    url(r'^pc_caipiao/$', TemplateView.as_view(template_name="pc_caipiao.jade")),
    #url(r'^september_activity/$', TemplateView.as_view(template_name="september_activity.jade")),
    url(r'^web-view/$', TemplateView.as_view(template_name="webView.html")),
    url(r'^web-center/$', TemplateView.as_view(template_name="fetchtoken.jade")),

    url(r'^android-view/$', TemplateView.as_view(template_name="android_view.html")),
    url(r'^new_user/$', TemplateView.as_view(template_name="new_user.jade")),
    url(r'^recommended/$', TemplateView.as_view(template_name="recommended.jade")),
    url(r'^national/$', TemplateView.as_view(template_name="national.jade")),
    url(r'^gold_two/$', TemplateView.as_view(template_name="gold_two.jade")),

    url(r'^baidu_finance/$', BaiduFinanceView.as_view(wx_classify='fwh', wx_code='bdjr'), name="baidu_finance"),
    url(r'^seckill/$', TemplateView.as_view(template_name="seckill.jade")),
    url(r'^november_new/$', TemplateView.as_view(template_name="november_new.jade")),
    url(r'^jucheng/$', TemplateView.as_view(template_name="jucheng.jade")),
    #url(r'^youku/$', TemplateView.as_view(template_name="youku_test.jade")),
    url(r'^two-eleven/$', TemplateView.as_view(template_name="two-eleven.jade")),
    url(r'^bid/$', TemplateView.as_view(template_name="bid.jade")),
    url(r'^365_gu/$', TemplateView.as_view(template_name="365_gu.jade")),
    #url(r'thanksgiving/$', TemplateView.as_view(template_name="thanksgiving.jade")),
    url(r'winter_brid/$', TemplateView.as_view(template_name="winter_bird.jade")),
    url(r'^xiaoher/$', TemplateView.as_view(template_name="xiaoher.jade")),
    url(r'fun_tuan/$', TemplateView.as_view(template_name="fun_tuan.jade")),
    url(r'noviceDecember/$', TemplateView.as_view(template_name="noviceDecember.jade")),
    url(r'^juchengtwo/$', TemplateView.as_view(template_name="juchengtwo.jade")),
    url(r'^damai/$', TemplateView.as_view(template_name="damai.jade")),
    url(r'^recharge_8000/$', TemplateView.as_view(template_name="recharge_8000.jade")),
    url(r'^double_eggs/$', TemplateView.as_view(template_name="double_eggs.jade")),
    url(r'^celebrity/$', TemplateView.as_view(template_name="celebrity.jade")),
    url(r'^xunlei_setp/$', ThunderTenAcvitityTemplate.as_view(wx_classify='fwh', wx_code='')),
    url(r'^xunlei_one/$', ThunderTenAcvitityTemplate.as_view(wx_classify='fwh', wx_code='')),
    url(r'^broken_million/$', TemplateView.as_view(template_name="broken_million.jade")),
    url(r'^damai-old/$', TemplateView.as_view(template_name="damai-old.jade")),
    url(r'^app_damai_old/$', TemplateView.as_view(template_name="app_damai_old.jade")),
    url(r'^send_reward/$', TemplateView.as_view(template_name="send_reward.jade")),
    url(r'^january_reward/$', TemplateView.as_view(template_name="january_reward.jade")),
    url(r'^damai-video/$', TemplateView.as_view(template_name="damai-video.jade")),
    url(r'^new_year/$', TemplateView.as_view(template_name="new_year.jade")),
    url(r'^life_style/$', TemplateView.as_view(template_name="life_style.jade")),
    url(r'^two-novice/$', TemplateView.as_view(template_name="two-novice.jade")),
    url(r'^brige/$', TemplateView.as_view(template_name="javascriptBrige.html")),
    url(r'^damai-back/$', TemplateView.as_view(template_name="damai-back.jade")),
    # url(r'^open_house/$', TemplateView.as_view(template_name="open_house.jade")),
    url(r'^open_house/$', OpenHouseApiView.as_view()),
    url(r'^airport_operation/$', TemplateView.as_view(template_name="airport_operation.jade")),
    # url(r'^spring_mobilization/$', TemplateView.as_view(template_name="spring_mobilization.jade")),
    url(r'^wangli_vip/$', TemplateView.as_view(template_name="wangli_vip.jade")),
    url(r'^august_phone/$', TemplateView.as_view(template_name="august_phone.jade")),
    url(r'^april_mobilization/$', TemplateView.as_view(template_name="april_mobilization.jade")),
    url(r'^open_day_review/$', HMDP2PListView.as_view(template_name="open_day_review.jade", p2p_list_url_name="p2p_list")),
    url(r'^center_film_ticket/$', TemplateView.as_view(template_name="center_film_ticket.jade")),
    url(r'^six_billion/(?P<template>\w+)/$', SixBillionView.as_view(), name="six_billion"),
    url(r'^car_house_loan/$', TemplateView.as_view(template_name="car_house_loan.jade")),
    url(r'^european_cup/$', TemplateView.as_view(template_name="european_cup.jade")),
    url(r'^love_on_july/$', TemplateView.as_view(template_name="love_on_july.jade")),

    url(r'^one_lifestyle/$', TemplateView.as_view(template_name="lifestyle.jade")),
    url(r'^xunlei_three/$', ThunderTenAcvitityTemplate.as_view(wx_classify='fwh', wx_code='')),
    url(r'^xunlei_treasure/$', ThunderTenAcvitityTemplate.as_view(wx_classify='fwh', wx_code='', template_name="xunlei.jade")),
    url(r'^shield_plan/$', ShieldPlanView.as_view()),
    url(r'^ihaomu/$', TemplateView.as_view(template_name="ihaomu.jade")),
    url(r"^chefangdai/$", CheFangDaiProductView.as_view()),
    url(r"^chefangdaiapp/$", CheFangDaiProductAPPView.as_view()),
    
)

# app URL
urlpatterns += patterns(
    '',
    url(r'^app_father/$', TemplateView.as_view(template_name="app_fatherday.jade")),
    url(r'^app_movie/$', TemplateView.as_view(template_name="app_movie.jade")),
    url(r'^app_level/$', TemplateView.as_view(template_name="app_level.jade")),
    url(r'^app_invite/$', TemplateView.as_view(template_name="app_invite.jade")),
    url(r'^app_shareReward/$', TemplateView.as_view(template_name="client_display.jade")),
    url(r'^app_request/$', TemplateView.as_view(template_name="app_request.jade")),
    url(r'^app_gold/$', TemplateView.as_view(template_name="app_gold_season.jade")),
    url(r'^app_july_act/$', TemplateView.as_view(template_name="app_july_act.jade")),
    url(r'^app_extension/$', TemplateView.as_view(template_name="app_extension.jade")),
#    url(r'^app_ele/$', TemplateView.as_view(template_name="app_ele.jade")),
    url(r'^app_eight_gift/$', TemplateView.as_view(template_name="app_eight_gift.jade")),
    url(r'^app_eight/$', TemplateView.as_view(template_name="app_eight.jade")),
    url(r'^xingmei/$', TemplateView.as_view(template_name="xingmei.jade")),
    url(r'^app_xingmei/$', TemplateView.as_view(template_name="app_xingmei.jade")),
    url(r'^app_xingmei_two/$', TemplateView.as_view(template_name="app_xingmei_two.jade")),
    url(r'^h5_gold/$', TemplateView.as_view(template_name="h5_gold.jade")),
    url(r'^app_qixi/$', TemplateView.as_view(template_name="app_qixi.jade")),
    url(r'^app_gold_day/$', TemplateView.as_view(template_name="app_gold_day.jade")),
    url(r'^app_pc_download/$', TemplateView.as_view(template_name="app_pc_download.jade")),
    url(r'^app_lottery/$', AppLotteryTemplate.as_view(template_name="app_lottery.jade"), name="app_lottery"),
    url(r'^lingcai/phone/$', OpenidPhoneForFencai.as_view()),
    url(r'^app_scratch/$', TemplateView.as_view(template_name="app_scratch.jade")),
    #url(r'^app_scratch_copy/$', login_required(TemplateView.as_view(template_name="app_scratch_copy.jade"), login_url='/accounts/token_login/')),
    url(r'^app_scratch_copy/$', TemplateView.as_view(template_name="app_scratch_copy.jade")),
    url(r'^app_national/$', TemplateView.as_view(template_name="app_national.jade")),
    url(r'^app_open_house/$', TemplateView.as_view(template_name="app_open_house.jade")),
    url(r'^h5_open_house/$', TemplateView.as_view(template_name="h5_open_house.jade")),
    #url(r'^app_airport_operation/$', fwh_login_required(TemplateView.as_view(template_name="app_airport_operation.jade"))),
    url(r'^app_airport_operation/$', TemplateView.as_view(template_name="app_airport_operation.jade")),


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


    url(r'^maimai_index/$', MaiMaiView.as_view(), name="maimai_index"),
    #url(r'^maimai_index/$', TemplateView.as_view(template_name="app_maimaiIndex.jade"), name='maimai_index'),
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
    url(r'^app_365_gu/$', TemplateView.as_view(template_name="app_365_gu.jade")),
    url(r'^app_xiaoher/$', TemplateView.as_view(template_name="app_xiaoher.jade")),

    url(r'^app-invite/$', TemplateView.as_view(template_name="app_invite_friends.jade")),
    url(r'^app-invite-success/$', TemplateView.as_view(template_name="app_invite_success.jade")),
    url(r'^app-invite-error/$', TemplateView.as_view(template_name="app_invite_error.jade")),
    url(r'^app-invite-server/$', TemplateView.as_view(template_name="app_invite_server.jade")),

    url(r'^app_thanksgiv/$', TemplateView.as_view(template_name="app_thanksgiv.jade")),
    url(r'^app_thanksgivin/$', TemplateView.as_view(template_name="app_thanksgivin.jade")),
    url(r'^app_noviceDecember_h5/$', TemplateView.as_view(template_name="app_noviceDecember_h5.jade")),
    url(r'^app_juchengtwo/$', TemplateView.as_view(template_name="app_juchengtwo.jade")),
    url(r'^app_recharge_8000/$', TemplateView.as_view(template_name="app_recharge_8000.jade")),
    url(r'^app_damai/$', TemplateView.as_view(template_name="app_damai.jade")),
    url(r'^app_double_eggs/$', TemplateView.as_view(template_name="app_double_eggs.jade")),
    url(r'^app_praise_reward/$', TemplateView.as_view(template_name="app_praise_reward.jade")),
    #url(r'^app_xunlei/$', ThunderTenAcvitityTemplate.as_view(template_name="app_xunlei.jade")),
    url(r'^app_xunlei/$', TemplateView.as_view(template_name="app_xunlei_new.jade")),
    url(r'^app_send_reward/$', TemplateView.as_view(template_name="app_send_reward.jade")),
    url(r'^app_january_reward/$', TemplateView.as_view(template_name="app_january_reward.jade")),
    # url(r'^app_thanksgivin/$', login_required(TemplateView.as_view(template_name="app_thanksgivin.jade"), login_url='/accounts/token_login/')),
    url(r'^app_wangli_vip/$', TemplateView.as_view(template_name="app_wangli_vip.jade")),
    url(r'^app_august_phone/$', TemplateView.as_view(template_name="app_august_phone.jade")),

    url(r'^weixin_mammon/$', TemplateView.as_view(template_name="h5_mammon.jade")),
    url(r'^app_two_novice/$', TemplateView.as_view(template_name="app_two_novice.jade")),

    url(r'^weixin_lifestyle/$', TemplateView.as_view(template_name="h5_lifestyle.jade")),
    url(r'^app_xunleithree/$', TemplateView.as_view(template_name="app_xunlei_new.jade")),
    url(r'^app_xunleizhuce/$', ThunderTenAcvitityTemplate.as_view(template_name="app_xunleizhuce.jade")),
    url(r'^h5_recruit/$', TemplateView.as_view(template_name="h5_recruit.jade")),
    url(r'^app_april_mobilization/$', TemplateView.as_view(template_name="app_april_mobilization.jade")),
    url(r'^new_user_gift/$', TemplateView.as_view(template_name="new_user_gift.jade")),
    url(r'^app_xunlei_treasure/$', ThunderTenAcvitityTemplate.as_view(wx_classify='fwh', wx_code='', template_name="app_xunlei_new.jade")),
    url(r'^app_open_day_review/$', HMDP2PListView.as_view(template_name="app_open_day_review.jade")),
    url(r'^dyh_open_day_review/$', HMDP2PListView.as_view(template_name="app_open_day_review.jade", p2p_list_url_name="weixin_p2p_list")),
    url(r'^app_yuelibao_is_come/$', HMDP2PListView.as_view(template_name="app_yuelibao_is_come.jade", p2p_list_url_name="weixin_p2p_list")),
    url(r'^app_center_film_ticket/$', TemplateView.as_view(template_name="app_center_film_ticket.jade")),
    #Comment by hb on 2016-05-31
    #url(r'^app_xunlei_welfare/$', TemplateView.as_view(template_name="app_xunlei_welfare.jade")),
    url(r'^new_user_gift/$', login_required(TemplateView.as_view(template_name="server_new_user_gift.jade"), login_url="/accounts/login/")),
    url(r'^app_pretty_reach_home/$', TemplateView.as_view(template_name="app_pretty_reach_home.jade")),
    # url(r'^app_xunleizhuce/$', TemplateView.as_view(template_name="app_xunleizhuce.jade")),
    url(r'^app_baby_box/h5/$', TemplateView.as_view(template_name="app_baby_box.jade")),

    url(r'^app_baby_box/ios/$', TemplateView.as_view(template_name="app_baby_box_ios.jade")),
    url(r'^app_baby_box/android/$', TemplateView.as_view(template_name="app_baby_box_android.jade")),
    url(r'^app_jack_shrimp/$', TemplateView.as_view(template_name="app_jack_shrimp.jade")),
    url(r'^app_car_house_loan/$', TemplateView.as_view(template_name="app_car_house_loan.jade")),
    url(r'^app_european_cup/$', TemplateView.as_view(template_name="app_european_cup.jade")),
    # url(r'^app_six_billion/$', TemplateView.as_view(template_name="app_six_billion.jade")),
    url(r'^app_bodybuilding/$', TemplateView.as_view(template_name="app_bodybuilding.jade")),
    url(r'^app_exercise/$', TemplateView.as_view(template_name="app_exercise.jade")),
    url(r'^app_love_on_july/$', TemplateView.as_view(template_name="app_love_on_july.jade")),

    # url(r'^festival_two/$', TemplateView.as_view(template_name="festival_two.html")),
    url(r'^h5_shield_plan/$', ShieldPlanH5View.as_view()),
    url(r'^load_wlb/$', TemplateView.as_view(template_name="load_wlb.jade")),

)
# app with webview
urlpatterns += patterns(
    '',
    url(r'^thanks/$', login_required(TemplateView.as_view(template_name="app_thanksgiv.jade"), login_url='/accounts/token_login/')),
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

urlpatterns += patterns(
    '',
    url(r'', include('experience_gold.urls'))
)

urlpatterns += patterns(
    '',
    url(r'^area/$', PcActivityAreaView.as_view()),
    url(r'^area/filter/$', ActivityAreaApi.as_view()),
)

urlpatterns += patterns(
    '',
    url(r'^thunder/binding/$', ThunderBindingApi.as_view()),
    url(r'^thunder/binding_query/$', ThunderBindingQueryApi.as_view()),
)
