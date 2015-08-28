#!/usr/bin/env python
# coding: utf-8

from django.contrib import admin
from django.utils import timezone
from wanglibao_redpack.models import RedPack, RedPackRecord, RedPackEvent, InterestHike
from import_export import resources, fields
from import_export.admin import ExportMixin


class RedPackEventAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("id", "name", "rtype", "red_amount", "invest_amount", "describe", "red_num", "give_mode", "give_platform", "apply_platform", "give_start_at", "give_end_at",
                    "available_at", "unavailable_at", "invalid", "created_at")
    search_fields = ("name", "give_mode")
    list_filter = ("give_mode","give_platform","apply_platform")

    def red_num(self, obj):
        return obj.value
    red_num.short_description = u"优惠券个数"

    def red_amount(self, obj):
        return obj.amount
    red_amount.short_description = u"优惠券金额"


class RedPackResource(resources.ModelResource):

    class Meta:
        model = RedPack
        fields = ('token',)


class RedPackAdmin(ExportMixin, admin.ModelAdmin):
    actions = None
    list_display = ("id", "event", "token", "status")
    search_fields = ("token","event__name")
    list_filter = ("status",)
    resource_class = RedPackResource

    def has_delete_permission(self, request, obj=None):
        return False

    # def has_add_permission(self, request):
    #     return False

    def get_readonly_fields(self, request, obj=None):
        return self.list_display


class RedPackRecordResource(resources.ModelResource):
    id = fields.Field(attribute="id", column_name=u"流水ID")
    redpack_id = fields.Field(attribute="redpack__event_id", column_name=u"优惠券ID")
    redpack = fields.Field(attribute="redpack__event__name", column_name=u"优惠券活动名称")
    change_platform = fields.Field(attribute="change_platform", column_name=u"兑换平台")
    apply_platform = fields.Field(attribute="apply_platform", column_name=u"使用平台")
    apply_at = fields.Field(attribute="apply_at", column_name=u"使用时间")
    apply_amount = fields.Field(attribute="apply_amount", column_name=u"使用金额")

    class Meta:
        model = RedPackRecord
        fields = ("id", "redpack_id", "redpack", "user", "change_platform", "apply_platform", "created_at",
                  "apply_amount", "apply_at", "order_id")

        export_order = ("id", "redpack_id", "redpack", "user", "change_platform", "apply_platform", "created_at",
                        "apply_amount", "apply_at", "order_id")

    def dehydrate_created_at(self, obj):
        return timezone.localtime(obj.created_at).strftime("%Y-%m-%d %H:%M:%S")

    def dehydrate_apply_at(self, obj):
        if obj.apply_at:
            return timezone.localtime(obj.apply_at).strftime("%Y-%m-%d %H:%M:%S")
        else:
            return obj.apply_at


class RedPackRecordAdmin(ExportMixin, admin.ModelAdmin):
    actions = None
    list_display = ("id", "redpack", "user", "change_platform", "apply_platform", "created_at",
                    "apply_amount", "apply_at", "order_id", "product_id")
    search_fields = ('user__wanglibaouserprofile__phone', 'redpack__event__name')
    raw_id_fields = ('user', "redpack")
    list_filter = ('change_platform', 'apply_platform', "apply_at", "created_at")
    resource_class = RedPackRecordResource

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return self.list_display

    def get_export_filename(self, file_format):
        date_str = timezone.now().strftime('%Y-%m-%d')
        filename = "%s-%s.%s" % (u"优惠券使用流水".encode('utf-8'),
                                 date_str,
                                 file_format.get_extension())
        return filename

class InterestHikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "rate", "intro_total", "invalid", "paid", 
                    "amount", "created_at")
    search_fields = ('user__wanglibaouserprofile__phone', 'product__name')
    raw_id_fields = ("user", "product")

admin.site.register(RedPack, RedPackAdmin)
admin.site.register(RedPackEvent, RedPackEventAdmin)
admin.site.register(RedPackRecord, RedPackRecordAdmin)
admin.site.register(InterestHike, InterestHikeAdmin)
