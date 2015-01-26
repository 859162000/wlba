from django.conf.urls import patterns, url
from views import RedPacketView

urlpatterns = patterns('',
    url(r'^$', RedPacketView.as_view()),
)
