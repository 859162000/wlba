#!/usr/bin/env python
# encoding:utf-8

from django.contrib import admin
from wanglibao_redpack.models import RedPack, RedPackRecord, RedPackEvent
from import_export import resources
from import_export.admin import ExportMixin



class RedPackEventAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "rtype", "red_amount", "invest_amount", "describe", "red_num", "give_mode", "give_platform", "apply_platform", "give_start_at", "give_end_at",
                    "available_at", "unavailable_at", "invalid", "created_at")
    search_fields = ("name", "give_mode")
    list_filter = ("give_mode","give_platform","apply_platform")

    def red_num(self, obj):
        return obj.value
    red_num.short_description = u"红包个数"

    def red_amount(self, obj):
        return obj.amount
    red_amount.short_description = u"红包金额"


class RedPackResource(resources.ModelResource):

    class Meta:
        model = RedPack
        fields = ('token',)

class RedPackAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ("id", "event", "token", "status")
    search_fields = ("token","event__name")
    list_filter = ("status",)
    resource_class = RedPackResource

class RedPackRecordAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ("id", "redpack", "user", "change_platform", "apply_platform", "created_at",
                    "apply_amount", "apply_at", "order_id")
    search_fields = ('user__wanglibaouserprofile__phone', 'redpack__event__name')
    raw_id_fields = ('user', "redpack")
    list_filter = ('change_platform', 'apply_platform')


admin.site.register(RedPack, RedPackAdmin)
admin.site.register(RedPackEvent, RedPackEventAdmin)
admin.site.register(RedPackRecord, RedPackRecordAdmin)
