from django.contrib import admin
from wanglibao_banner.models import Banner, Partner


class BannerAdmin(admin.ModelAdmin):
    list_display = ('name', 'device', 'type', 'priority')
    list_editable = ('priority',)


class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'link', 'alt', 'priority')
    list_editable = ('priority',)

admin.site.register(Banner, BannerAdmin)
admin.site.register(Partner, PartnerAdmin)
