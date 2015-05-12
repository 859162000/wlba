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
    url(r'^wap/02/$', TemplateView.as_view(template_name="xunlei_02.jade")),
    url(r'^wap/03/$', TemplateView.as_view(template_name="xunlei_03.jade")),
    url(r'^kuaipan/$', TemplateView.as_view(template_name="kuaipan.jade")),
    url(r'^fengxing/$', TemplateView.as_view(template_name="fengxing.jade")),
    #url(r'^wlbtvsstsiis/tv/$', TemplateView.as_view(template_name="tv.jade")),
    url(r'^app_share/$', TemplateView.as_view(template_name="activity_app_share.jade")),
    url(r'^wap/share$', AppShareView.as_view(), name="app_share"),
    url(r'^wap/share_reg/$', AppShareRegView.as_view(), name="app_share_reg"),
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
    url(r'^full_xin/$', TemplateView.as_view(template_name="full_xin.jade")),
    # url(r'^list_day/$', TemplateView.as_view(template_name="list_day.jade")),
    url(r'^list_history/$', TemplateView.as_view(template_name="list_history.jade")),
    url(r'^day_mobile/$', TemplateView.as_view(template_name="day_mobile.jade")),
    url(r'^app_movie/$', TemplateView.as_view(template_name="app_movie.jade")),
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

