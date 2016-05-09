# encoding: utf8

import json
from django.contrib import admin
from .tasks import common_callback
from .utils import get_bajinshe_access_token
from .models import CallbackRecord

LOCAL_VAR = locals()


def update_bajinshe_recallback_data(order_id, channel, data):
    data = json.loads(data)
    data['access_token'] = get_bajinshe_access_token(order_id)
    data = json.dumps(data)

    call_back_record = CallbackRecord.objects.filter(callback_to=channel, order_id=order_id).first()
    if call_back_record:
        call_back_record.request_data = json.dumps(data)
        call_back_record.save()

    return data


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

            update_coop_recallback_data = LOCAL_VAR['update_%s_recallback_data' % obj.callback_to.lower()]
            if update_coop_recallback_data:
                data = update_coop_recallback_data(obj.order_id, obj.callback_to, json.loads(obj.request_data))
            else:
                data = json.loads(obj.request_data)

            common_callback(channel=obj.callback_to,
                            url=obj.request_url,
                            params=data,
                            headers=headers,
                            order_id=obj.order_id,
                            ret_parser=obj.ret_parser)
        else:
            obj.save()


admin.site.register(CallbackRecord, CallbackRecordAdmin)
