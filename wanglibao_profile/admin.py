# coding=utf-8

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import ActivityUserInfo
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

admin.site.register(ActivityUserInfo, ActivityUserInfoAdmin)
