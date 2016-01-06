# coding=utf-8

from django.contrib import admin
from wanglibao_qiye.models import EnterpriseUserProfile


class EnterpriseProfileAdmin(admin.ModelAdmin):
    pass
    actions = None
    list_display = ('user', 'company_name', 'status', 'description', 'modify_time', 'created_time')
    search_fields = ('user_id', 'user__wanglibaouserprofile__phone')
    raw_id_fields = ('user', 'bank')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        has_change_fields = ('status', 'description')
        return has_change_fields


admin.site.register(EnterpriseUserProfile, EnterpriseProfileAdmin)