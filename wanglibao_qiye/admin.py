# coding=utf-8

from django.contrib import admin
from wanglibao_qiye.models import EnterpriseUserProfile


class EnterpriseProfileAdmin(admin.ModelAdmin):
    pass
    # actions = None
    # search_fields = ('user_id', 'user__wanglibaouserprofile__phone')
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False
    #
    # def has_add_permission(self, request):
    #     return False


admin.site.register(EnterpriseUserProfile, EnterpriseProfileAdmin)