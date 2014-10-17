from django.conf.urls import patterns, url
from django.views.generic import TemplateView, RedirectView


urlpatterns = patterns(
    '',
    url(r'^invite/$', TemplateView.as_view(template_name="activity_invite.jade")),
    url(r'^xunlei/$', TemplateView.as_view(template_name="xunlei.jade")),
)