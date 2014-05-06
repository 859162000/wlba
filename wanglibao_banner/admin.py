from django.contrib import admin
from wanglibao_banner.models import Banner


class BannerAdmin(admin.ModelAdmin):
    list_display = ('name', 'device', 'type', 'priority')

admin.site.register(Banner, BannerAdmin)
