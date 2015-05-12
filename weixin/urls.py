# encoding:utf-8
from django.conf.urls import patterns, url
from django.views.generic import TemplateView, RedirectView
import views

urlpatterns = patterns(
    '',
    url(r'^connect/(?P<id>\w+)/', views.ConnectView.as_view()),
    url(r'^list/', views.P2PListView.as_view(), name='weixin_p2p_list'),
    url(r'^account/', TemplateView.as_view(template_name="weixin_account.jade")),
    url(r'^detail/(?P<id>\w+)', views.P2PDetailView.as_view(), name='weixin_p2p_detail'),
)
