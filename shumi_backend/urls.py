from django.conf.urls import patterns, url

from views import OAuthCallbackView

urlpatterns = patterns('',
    url(r'^callback/(?P<pk>\d+)/$', OAuthCallbackView.as_view(), name='callback-view'),
)