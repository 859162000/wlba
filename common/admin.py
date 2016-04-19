# encoding: utf8

from django.contrib import admin
from .models import CallbackRecord


class CallbackRecordAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("user", "callback_to", "order_id", "third_order_id",
                    "description", "result_code", "result_msg", "answer_at", "created_at")
    search_fields = ('user_id', 'user__wanglibaouserprofile__phone', "order_id",
                     'third_order_id', 'callback_to')
    raw_id_fields = ('user', )

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(CallbackRecord, CallbackRecordAdmin)
