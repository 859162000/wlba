# coding=utf-8

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ExportMixin
from .models import ActivityUserInfo, RepeatPaymentUser, RepeatPaymentUserRecords
from .forms import ActivityUserInfoForm


class RewardResource(resources.ModelResource):
    class Meta:
        model = ActivityUserInfo
        fields = ('id', 'name', 'phone', 'address', 'is_wlb_phone', 'extra', 'created_at', 'updated_at')

    def import_obj(self, instance, row, False):
        super(RewardResource, self).import_obj(instance, row, False)


class ActivityUserInfoAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    actions = None
    list_display = ('id', 'name', 'phone', 'address', 'is_wlb_phone', 'extra', 'created_at')
    search_fields = ('phone', 'name')
    form = ActivityUserInfoForm
    resource_class = RewardResource


class RepeatPaymentUserAdmin(ImportExportModelAdmin):
    list_display = ('user_id', 'name', 'phone', 'amount', 'is_every_day', 'product_ids')
    search_fields = ('name', 'phone')


class RepeatPaymentUserRecordsAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('user_id', 'name', 'phone', 'amount', 'amount_current', 'description', 'create_time')
    search_fields = ('name', 'phone')

admin.site.register(ActivityUserInfo, ActivityUserInfoAdmin)
admin.site.register(RepeatPaymentUser, RepeatPaymentUserAdmin)
admin.site.register(RepeatPaymentUserRecords, RepeatPaymentUserRecordsAdmin)
