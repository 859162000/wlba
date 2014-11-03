from django.conf.urls import patterns, url
from views import AnnouncementHomeView, AnnouncementDetailView


urlpatterns = patterns(
    '',
    url(r'^$', AnnouncementHomeView.as_view(), name='announcement_home'),
    url(r'^detail/(?P<id>\w+)$', AnnouncementDetailView.as_view(), name='announcement_detail'),
)