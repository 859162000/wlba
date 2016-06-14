# encoding:utf-8
from django.contrib import admin
from wanglibao_banner.models import Banner, Partner, Hiring, Aboutus, AppActivate, AboutDynamic
from django.conf import settings

class BannerAdmin(admin.ModelAdmin):
    list_display = ('name', 'device', 'type', 'priority', 'is_long_used', 'start_at', 'end_at', 'is_used')
    list_editable = ('priority',)


class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'link', 'alt', 'priority')
    list_editable = ('priority',)


class HiringAdmin(admin.ModelAdmin):
    list_display = ('name', 'position_types', 'is_urgent', 'is_hide', 'priority')
    list_editable = ('priority',)


class AboutusAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'code')


class AppActivateAdmin(admin.ModelAdmin):
    list_display = ('name', 'device', 'img_one_url', 'priority', 'last_updated', 'is_long_used', 'start_at', 'end_at', 'is_used', )

    def img_one_url(self, obj):

        url = settings.CALLBACK_HOST+"/media/" + obj.img_one.name
        return '<a href="{url}" target="_blank">点击查看</a>'.format(url=url)
    img_one_url.short_description = u'大图片'
    img_one_url.allow_tags = True

class AboutDynamicAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'priority', 'hide_in_list', 'updated_time')
    fields = ('title', 'description', 'content', 'priority', 'hide_in_list', 'start_time', 'end_time')


admin.site.register(Banner, BannerAdmin)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(Hiring, HiringAdmin)
admin.site.register(Aboutus, AboutusAdmin)
admin.site.register(AppActivate, AppActivateAdmin)
admin.site.register(AboutDynamic, AboutDynamicAdmin)
