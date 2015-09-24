from django.conf.urls import patterns, url
from views import RedPacketView
from wanglibao_redpack.views import ApplyRedPacketAPIView

urlpatterns = patterns('',
    url(r'^$', RedPacketView.as_view()),
    url(r'^apply/$', ApplyRedPacketAPIView.as_view()),
)
