#!/usr/bin/env python
# encoding:utf-8

from django.contrib import admin
from wanglibao_redpack.models import RedPack, RedPackRecord, RedPackEvent
from import_export import resources
from import_export.admin import ExportMixin



class RedPackEventAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "rtype", "amount", "invest_amount", "describe", "value", "give_mode", "give_start_at", "give_end_at",
                    "available_at", "unavailable_at", "invalid", "created_at")
    search_fields = ("name", "give_mode")


class RedPackResource(resources.ModelResource):

    class Meta:
        model = RedPack
        fields = ('token',)

class RedPackAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ("id", "event", "token", "status")
    search_fields = ("token", "event__id")
    resource_class = RedPackResource

class RedPackRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "redpack", "user", "change_platform", "apply_platform", "created_at", "apply_at", "order_id")
    search_fields = ('user__wanglibaouserprofile__phone',)
    raw_id_fields = ('user', "redpack")


admin.site.register(RedPack, RedPackAdmin)
admin.site.register(RedPackEvent, RedPackEventAdmin)
admin.site.register(RedPackRecord, RedPackRecordAdmin)
