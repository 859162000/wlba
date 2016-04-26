# encoding: utf8

import json
from django.contrib import admin
from .tasks import common_callback
from .models import CallbackRecord


class CallbackRecordAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("user", "callback_to", "order_id", "third_order_id",
                    "description", "result_code", "result_msg", "answer_at", "created_at")
    search_fields = ('user__id', 'user__wanglibaouserprofile__phone', "order_id",
                     'third_order_id', 'callback_to')
    raw_id_fields = ('user', )

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        # 管理后台回调补发/重发
        if obj.re_callback is True:
            obj.re_callback = False
            headers = obj.request_headers
            headers = json.loads(headers) if headers else headers
            common_callback.apply_async(
                countdown=3,
                kwargs={'channel': obj.callback_to,
                        'url': obj.request_url,
                        'params': json.loads(obj.request_data),
                        'headers': headers,
                        'order_id': obj.order_id,
                        'ret_parser': obj.ret_parser,
                        }
            )

        obj.save()


admin.site.register(CallbackRecord, CallbackRecordAdmin)
