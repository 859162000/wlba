from django.contrib import admin
from models import Activity, ActivityRule, ActivityRecord


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'platform', 'product_cats', 'product_ids', 'description',\
                    'start_at', 'end_at', 'status', 'priority')


class ActivityRuleAdmin(admin.ModelAdmin):
    list_display = ('activity', 'rule_name', 'rule_description', 'trigger_node', 'gift_type', 'redpack', \
                    'reward', 'income', 'min_amount', 'max_amount')


admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityRule, ActivityRuleAdmin)