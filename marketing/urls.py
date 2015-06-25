from django.conf.urls import patterns, url
from django.views.generic import TemplateView, RedirectView
from marketing.views import AppShareView, AppShareRegView, NewYearView, AggregateView, IntroducedAwardTemplate
from play_list import Investment, InvestmentHistory, InvestmentRewardView
from django.contrib.auth.decorators import login_required

urlpatterns = patterns(
    '',
    url(r'^invite/$', TemplateView.as_view(template_name="activity_invite.jade")),
    url(r'^xunlei/$', TemplateView.as_view(template_name="xunlei.jade")),
    url(r'^gold/$', TemplateView.as_view(template_name="gold.jade")),
    url(r'^firecoin/$', TemplateView.as_view(template_name="firecoin.jade")),
    url(r'^wap/01/$', TemplateView.as_view(template_name="xunlei_01.jade")),
    #url(r'^wap/02/$', TemplateView.as_view(template_name="xunlei_02.jade")),
    url(r'^wap/03/$', TemplateView.as_view(template_name="xunlei_03.jade")),
    url(r'^kuaipan/$', TemplateView.as_view(template_name="kuaipan.jade")),
    url(r'^fengxing/$', TemplateView.as_view(template_name="fengxing.jade")),
    #url(r'^wlbtvsstsiis/tv/$', TemplateView.as_view(template_name="tv.jade")),
    url(r'^app_share/$', TemplateView.as_view(template_name="activity_app_share.jade")),
    url(r'^wap/share$', AppShareView.as_view(), name="app_share"),
    url(r'^wap/share_reg/$', AppShareRegView.as_view(), name="app_share_reg"),
    url(r'^share_reg_new/$', TemplateView.as_view(template_name="app_share_reg_new.jade")),
    url(r'^share_regnew_href/$', TemplateView.as_view(template_name="share_regnew_href.jade")),
    url(r'^wap/agreement/$', TemplateView.as_view(template_name="app_agreement.jade")),
    url(r'^newyear/$', NewYearView.as_view(), name="new year"),
    url(r'^shengyan/$', TemplateView.as_view(template_name="shengyan.jade")),
    url(r'^app_shengyan/$', TemplateView.as_view(template_name="shengyan_h5.jade")),
    url(r'^xunleidenglu/$', TemplateView.as_view(template_name="xunleiredpack.jade")),
    url(r'^app_new/$', TemplateView.as_view(template_name="app_new_user.jade")),
    url(r'^history/$', TemplateView.as_view(template_name="day_history.jade")),
    url(r'^pptv_redpack/$', TemplateView.as_view(template_name="pptv_redpack.jade")),
    url(r'^app_day/$', TemplateView.as_view(template_name="app_day.jade")),
    url(r'^app_full/$', TemplateView.as_view(template_name="app_full.jade")),
    url(r'^app_fullNew/$', TemplateView.as_view(template_name="app_fullNew.jade")),
    url(r'^aiqiyi_redpack/$', TemplateView.as_view(template_name="aiqiyi_redpack.jade")),
    url(r'^full/$', TemplateView.as_view(template_name="full_get.jade")),
    url(r'^full_new/$', TemplateView.as_view(template_name="full_getNew.jade")),
    url(r'^xunleiredpack/$', TemplateView.as_view(template_name="xunleiredpack2.jade")),
    url(r'^full_login/$', TemplateView.as_view(template_name="fullLogin.jade")),
    url(r'^day_login/$', TemplateView.as_view(template_name="dayLogin.jade")),
    #url(r'^full_xin/$', TemplateView.as_view(template_name="full_xin.jade")),
    url(r'^full_send/$', TemplateView.as_view(template_name="full_send.jade")),
    # url(r'^list_day/$', TemplateView.as_view(template_name="list_day.jade")),
    url(r'^list_history/$', TemplateView.as_view(template_name="list_history.jade")),
    url(r'^day_mobile/$', TemplateView.as_view(template_name="day_mobile.jade")),
    url(r'^app_movie/$', TemplateView.as_view(template_name="app_movie.jade")),
    url(r'^ko_movie/$', TemplateView.as_view(template_name="ko_movie.jade")),
    url(r'^movie_login/$', TemplateView.as_view(template_name="app_movie_login.jade")),
    url(r'^agree_xieyi/$', TemplateView.as_view(template_name="agree_xieyi.jade")),
    url(r'^list_level/$', TemplateView.as_view(template_name="list_level.jade")),
    url(r'^app_level/$', TemplateView.as_view(template_name="app_level.jade")),
    url(r'^app_invite/$', TemplateView.as_view(template_name="app_invite.jade")),
    url(r'^app_shareReward/$', TemplateView.as_view(template_name="app_shareReward.jade")),
    url(r'^father_day/$', TemplateView.as_view(template_name="father_day.jade")),
    # url(r'^summer/$', TemplateView.as_view(template_name="summer.jade")),
    # url(r'^app_summer/$', TemplateView.as_view(template_name="app_summer.jade")),
    url(r'^newxunlei/$', TemplateView.as_view(template_name="newxunlei.jade")),
    url(r'^father/$', TemplateView.as_view(template_name="app_fatherday.jade")),
    url(r'^weipai/$', TemplateView.as_view(template_name="app_share_weipai.jade")),
    url(r'^app_gold/$', TemplateView.as_view(template_name="app_gold.jade")),
    url(r'^pan_gold/$', TemplateView.as_view(template_name="pan_gold.jade")),
)

urlpatterns += patterns(
    '',
    url(r'^aggregate/', AggregateView.as_view(template_name="aggregate.jade")),
    url(r'^new_user/$', TemplateView.as_view(template_name="new_user.jade")),
)

urlpatterns += patterns(
    '',
    url(r'^introduced_by/$', IntroducedAwardTemplate.as_view(template_name="introduced_by.jade")),
    url(r'^investment_reward/$', InvestmentRewardView.as_view(template_name="investment_reward.jade")),
    url(r'^investment/$', Investment.as_view(), name='day'),
    # url(r'^list_day/$', Investment.as_view(), name='list_day'),
)

