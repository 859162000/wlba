# coding: utf-8

from django.contrib import admin
from django.contrib.admin.filters import DateFieldListFilter, FieldListFilter, ChoicesFieldListFilter
import datetime
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.forms import formsets
from django.utils import timezone
from import_export.admin import ExportMixin
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


class CustomDateFilter(admin.SimpleListFilter):
    title = _(u'触发时间')
    parameter_name = u'trigger_at'

    def lookups(self, request, model_admin):
        return (
            ('today', _(u'今天')),
            ('yesterday', _(u'昨天')),
            ('before_yesterday', _(u'前天'))
        )

    def queryset(self, request, queryset):
        dt = datetime.datetime.now()
        if self.value() == 'today':
            return queryset.filter(trigger_at__gte=timezone.datetime(dt.year, dt.month, dt.day),
                                   trigger_at__lt=timezone.datetime(dt.year, dt.month, dt.day, 23, 59, 59))
        if self.value() == 'yesterday':
            return queryset.filter(trigger_at__gte=timezone.datetime(dt.year, dt.month, dt.day - 1),
                                   trigger_at__lt=timezone.datetime(dt.year, dt.month, dt.day - 1, 23, 59, 59))
        if self.value() == 'before_yesterday':
            return queryset.filter(trigger_at__gte=timezone.datetime(dt.year, dt.month, dt.day - 2),
                                   trigger_at__lt=timezone.datetime(dt.year, dt.month, dt.day - 2, 23, 59, 59))


class ActivityRecordAdmin(ExportMixin, admin.ModelAdmin):
    actions = None
    list_display = ('id', 'activity', 'rule', 'platform', 'trigger_node', 'msg_type', \
                    'send_type', 'description', 'user', 'income', 'trigger_at')
    list_filter = (
        'platform', 'trigger_node', 'msg_type', 'send_type',
        CustomDateFilter
    )
    search_fields = ('activity__name', 'rule__rule_name', 'user__wanglibaouserprofile__phone')

    # def __init__(self, *args, **kwargs):
    #     super(ActivityRecordAdmin, self).__init__(*args, **kwargs)
    #     self.list_display_links = (None, )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ActivityImagesAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('name', 'img_type', 'img', 'desc_one', 'desc_two', 'priority')}),
    )

    ordering = ('-img_type', '-priority')


class ActivityTemplatesAdmin(admin.ModelAdmin):

    list_display = ('id', 'name', 'banner')

    ordering = ('id',)

    # fieldsets = (
    #     (None, {'fields': ('name', )}),
    #     ('logo', {'fields': ('logo', 'logo_other', 'location')}),
    #     ('banner and login', {'fields': ('banner', 'is_login')}),
    #     (u'活动时间及描述模块', {'fields': ('is_activity_desc', 'desc', 'desc_time'), 'classes': ['collapse']}),
    #     (u'奖品图片和描述模块', {'fields': ('is_reward', 'reward_img', 'reward_desc'), 'classes': ['collapse']}),
    #     (u'邀请好友模块', {'fields': ['is_introduce', 'introduce_img', 'introduce_desc'], 'classes': ['collapse']}),
    #     (u'新手投资模块', {'fields': ('is_teacher', 'teacher_desc'), 'classes': ['collapse']}),
    #     (u'活动使用规则模块', {'fields': ('is_rule_use', 'rule_use'), 'classes': ['collapse']}),
    #     (u'活动规则模块', {'fields': ('is_rule_activity', 'rule_activity'), 'classes': ['collapse']}),
    #     (u'奖品发放规则模块', {'fields': ('is_rule_reward', 'rule_reward'), 'classes': ['collapse']}),
    #     (u'底部背景颜色模块', {'fields': ('is_footer', 'footer_color'), 'classes': ['collapse']}),
    # )

admin.site.register(ActivityImages, ActivityImagesAdmin)
admin.site.register(ActivityTemplates, ActivityTemplatesAdmin)

admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityRule, ActivityRuleAdmin)
admin.site.register(ActivityRecord, ActivityRecordAdmin)