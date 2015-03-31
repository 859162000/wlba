# coding: utf-8

from django.contrib import admin
from django import forms
from django.forms import formsets
from django.utils import timezone
from models import Activity, ActivityRule, ActivityRecord, ActivityTemplates, ActivityImages

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'platform', 'product_cats', 'product_ids',\
                    'channel', 'description', 'start_at', 'end_at', \
                    'activity_status', 'is_stopped', 'priority')
    search_fields = ('name', 'channel')
    list_filter = ('category', 'platform', 'is_stopped')


class ActivityRuleAdmin(admin.ModelAdmin):
    list_display = ('activity', 'rule_name', 'rule_description', 'trigger_node', 'gift_type',\
                    'redpack', 'reward', 'income', 'min_amount', 'max_amount', 'is_used')
    list_filter = ('trigger_node', 'gift_type', 'is_used')
    search_fields = ('rule_name', 'activity__name')


class ActivityRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'activity', 'rule', 'platform', 'trigger_node', 'msg_type', \
                    'send_type', 'description', 'user', 'income', 'created_at')
    list_filter = ('platform', 'trigger_node', 'msg_type', 'send_type',)
    search_fields = ('activity__name', 'rule__rule_name', 'user__wanglibaouserprofile__phone')

    def has_add_permission(self, request):
        return False


class ActivityImagesAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('name', 'img_type', 'img', 'desc_one', 'desc_two', 'priority')}),
    )
    # ordering = ('-img_type', '-priority')


class ActivityTemplatesAdmin(admin.ModelAdmin):

    list_display = ('id', )

    fieldsets = (
        (None, {'fields': ('name', )}),
        ('logo', {'fields': ('logo', 'logo_other', 'location')}),
        ('banner', {'fields': ('banner',)}),
        (u'活动时间及描述模块', {'fields': ('is_activity_desc', 'desc', 'desc_time'), 'classes': ['collapse']}),
        (u'奖品图片和描述模块', {'fields': ('is_reward', 'reward_img', 'reward_desc'), 'classes': ['collapse']}),
        (u'邀请好友模块', {'fields': ['is_introduce', 'introduce_img', 'introduce_desc'], 'classes': ['collapse']}),
        (u'新手投资模块', {'fields': ('is_teacher', 'teacher_desc'), 'classes': ['collapse']}),
        (u'活动使用规则模块', {'fields': ('is_rule_use', 'rule_use'), 'classes': ['collapse']}),
        (u'活动规则模块', {'fields': ('is_rule_activity', 'rule_activity'), 'classes': ['collapse']}),
        (u'奖品发放规则模块', {'fields': ('is_rule_reward', 'rule_reward'), 'classes': ['collapse']}),
    )

admin.site.register(ActivityImages, ActivityImagesAdmin)
admin.site.register(ActivityTemplates, ActivityTemplatesAdmin)

admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityRule, ActivityRuleAdmin)
admin.site.register(ActivityRecord, ActivityRecordAdmin)