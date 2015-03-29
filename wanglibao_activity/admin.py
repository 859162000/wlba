from django.contrib import admin
from django import forms
from django.forms import formsets
from django.utils import timezone
from models import Activity, ActivityRule, ActivityRecord

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'platform', 'product_cats', 'product_ids',\
                    'channel', 'description', 'start_at', 'end_at', \
                    'activity_status', 'is_stopped', 'priority')


class ActivityRuleAdmin(admin.ModelAdmin):
    list_display = ('activity', 'rule_name', 'rule_description', 'trigger_node', 'gift_type',\
                    'redpack', 'reward', 'income', 'min_amount', 'max_amount', 'is_used')


class ActivityRecordAdmin(admin.ModelAdmin):
    list_display = ('activity', 'rule', 'platform', 'trigger_node', 'msg_type', 'send_type', \
                    'description', 'user', 'income', 'created_at')

    def has_add_permission(self, request):
        return False


admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityRule, ActivityRuleAdmin)
admin.site.register(ActivityRecord, ActivityRecordAdmin)