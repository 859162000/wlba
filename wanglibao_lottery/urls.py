from django.conf.urls import patterns, url
from wanglibao_lottery.views import LotteryIssue, LotteryOpen

urlpatterns = patterns('',
    url(r'^issue/$', LotteryIssue.as_view()),
    url(r'^open/$', LotteryOpen.as_view())
)