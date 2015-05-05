from django.contrib import admin
from wanglibao_banner.models import Banner, Partner, Hiring, Aboutus


class BannerAdmin(admin.ModelAdmin):
    list_display = ('name', 'device', 'type', 'priority', 'is_long_used', 'start_at', 'end_at', 'is_used')
    list_editable = ('priority',)


class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'link', 'alt', 'priority')
    list_editable = ('priority',)


class HiringAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_urgent', 'is_hide', 'priority')
    list_editable = ('priority',)


class AboutusAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'code')


admin.site.register(Banner, BannerAdmin)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(Hiring, HiringAdmin)
admin.site.register(Aboutus, AboutusAdmin)
