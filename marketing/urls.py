from django.conf.urls import patterns, url
from django.views.generic import TemplateView, RedirectView
from marketing.views import AppShareView, AppShareRegView, NewYearView, AggregateView, IntroducedAwardTemplate
from play_list import Investment, InvestmentHistory, InvestmentRewardView
from django.contrib.auth.decorators import login_required

urlpatterns = patterns(
    '',
    url(r'^wap/share/$', AppShareView.as_view(), name="app_share"),
    url(r'^wap/share_reg/$', AppShareRegView.as_view(), name="app_share_reg"),
    url(r'^share_reg_new/$', TemplateView.as_view(template_name="app_share_reg_new.jade")),
    url(r'^share_regnew_href/$', TemplateView.as_view(template_name="share_regnew_href.jade")),
    url(r'^wap/agreement/$', TemplateView.as_view(template_name="app_agreement.jade")),
    url(r'^full_send/$', TemplateView.as_view(template_name="full_send.jade")),
    url(r'^ko_movie/$', TemplateView.as_view(template_name="ko_movie.jade")),
    url(r'^movie_login/$', TemplateView.as_view(template_name="app_movie_login.jade")),
    url(r'^agree_xieyi/$', TemplateView.as_view(template_name="agree_xieyi.jade")),
    url(r'^list_level/$', TemplateView.as_view(template_name="list_level.jade")),
    url(r'^father_day/$', TemplateView.as_view(template_name="father_day.jade")),
    url(r'^newxunlei/$', TemplateView.as_view(template_name="newxunlei.jade")),
    url(r'^father/$', TemplateView.as_view(template_name="app_fatherday.jade")),
    url(r'^weipai/$', TemplateView.as_view(template_name="app_share_weipai.jade")),
    url(r'^pan_gold/$', TemplateView.as_view(template_name="pan_gold.jade")),
    url(r'^july_act/$', TemplateView.as_view(template_name="july_act.jade")),
    url(r'^act_invite/$', TemplateView.as_view(template_name="act_invite.jade")),
    url(r'^ganjiwang/$', TemplateView.as_view(template_name="ganjiwang.jade")),
    url(r'^xunlei-august/$', TemplateView.as_view(template_name="xunlei-august.jade")),
)

# app URL
urlpatterns += patterns(
    '',
    url(r'^app_movie/$', TemplateView.as_view(template_name="app_movie.jade")),
    url(r'^app_level/$', TemplateView.as_view(template_name="app_level.jade")),
    url(r'^app_invite/$', TemplateView.as_view(template_name="app_invite.jade")),
    url(r'^app_shareReward/$', TemplateView.as_view(template_name="app_shareReward.jade")),
    url(r'^app_request/$', TemplateView.as_view(template_name="app_request.jade")),
    url(r'^app_gold/$', TemplateView.as_view(template_name="app_gold.jade")),
    url(r'^app_july_act/$', TemplateView.as_view(template_name="app_july_act.jade")),
    url(r'^app_extension/$', TemplateView.as_view(template_name="app_extension.jade")),
)

urlpatterns += patterns(
    '',
    url(r'^aggregate/', AggregateView.as_view(template_name="aggregate.jade")),
)

urlpatterns += patterns(
    '',
    url(r'^introduced_by/$', IntroducedAwardTemplate.as_view(template_name="introduced_by.jade")),
    url(r'^investment_reward/$', InvestmentRewardView.as_view(template_name="investment_reward.jade")),
    url(r'^investment/$', Investment.as_view(), name='day'),
)

urlpatterns += patterns('',
    url(r'^xunlei/july/$', TemplateView.as_view(template_name="xunlei_july.jade"), name='xunlei_july_activity')
)