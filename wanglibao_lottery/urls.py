from django.conf.urls import patterns, url
from wanglibao_lottery.views import LotteryList, LotteryDetail, LotteryIssue, LotteryOpen

urlpatterns = patterns('',
    url(r'^list/$', LotteryList.as_view()),
    url(r'^detail/$', LotteryDetail.as_view()),
    url(r'^issue/$', LotteryIssue.as_view()),
    url(r'^open/$', LotteryOpen.as_view())
)