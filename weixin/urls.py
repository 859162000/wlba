from django.conf.urls import patterns, url
from weixin.views import WeiXinView

urlpatterns = patterns('',
    url(r'^$', WeiXinView.as_view(), name='weixin-view'),
)