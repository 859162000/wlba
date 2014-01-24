from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^api/', include('wanglibao_rest.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

