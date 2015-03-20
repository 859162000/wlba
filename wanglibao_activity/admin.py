from django.contrib import admin
from django import forms
from django.forms import formsets
from django.utils import timezone
from models import Activity, ActivityRule, ActivityRecord

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'platform', 'product_cats', 'product_ids', 'description',\
                    'start_at', 'end_at', 'is_stopped', 'priority')


class ActivityRuleAdmin(admin.ModelAdmin):
    list_display = ('activity', 'rule_name', 'rule_description', 'trigger_node', 'gift_type', 'redpack', \
                    'reward', 'income', 'min_amount', 'max_amount')


class ActivityRecordAdmin(admin.ModelAdmin):
    list_display = ('activity', 'rule', 'platform', 'trigger_node', 'description', 'user', 'income', 'created_at')


admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityRule, ActivityRuleAdmin)
admin.site.register(ActivityRecord, ActivityRecordAdmin)