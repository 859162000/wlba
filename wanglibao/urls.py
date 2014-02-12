from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import login
from django.views.generic import TemplateView
from wanglibao.forms import EmailOrPhoneAuthenticationForm
from wanglibao.views import RegisterView

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name="index.html")),
    url(r'^trust/home$', TemplateView.as_view(template_name="trust_home.html"), name="trust_home"),
    url(r'^api/', include('wanglibao_rest.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {
            "template_name": "login.html",
            "authentication_form": EmailOrPhoneAuthenticationForm,
        }),
    url(r'^accounts/register/$', RegisterView.as_view()),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
)
