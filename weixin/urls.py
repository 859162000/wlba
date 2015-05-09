# encoding:utf-8
from django.conf.urls import patterns, url
import views

urlpatterns = patterns(
    '',
    url(r'^connect/(?P<id>\w+)/', views.ConnectView.as_view()),
)
