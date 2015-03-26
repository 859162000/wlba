# coding: utf-8

from django.contrib import admin
from django import forms
from django.forms import formsets
from django.utils import timezone
from models import Activity, ActivityRule, ActivityRecord, ActivityTemplates, TemplatesImages

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'platform', 'product_cats', 'product_ids',\
                    'channel', 'description', 'start_at', 'end_at', 'is_stopped', 'priority')


class ActivityRuleAdmin(admin.ModelAdmin):
    list_display = ('activity', 'rule_name', 'rule_description', 'trigger_node', 'gift_type',\
                    'redpack', 'reward', 'income', 'min_amount', 'max_amount', 'is_used')


class ActivityRecordAdmin(admin.ModelAdmin):
    list_display = ('activity', 'rule', 'platform', 'trigger_node', 'description', 'user',\
                    'income', 'created_at')


class TemplatesImageInline(admin.TabularInline):
    model = TemplatesImages
    # fields = ('name', 'img', 'desc_one', 'desc_two', 'priority')
    model.img_type = 'reward'
    extra = 3
    max_num = 6
    verbose_name = u'赠品礼包'
    verbose_name_plural = u'赠品礼包'

    def get_queryset(self, request):
        return super(TemplatesImageInline, self).get_queryset(request).filter(img_type='reward').order_by('-priority')


class TemplatesRegisterInline(admin.TabularInline):
    model = TemplatesImages
    # fields = ('name', 'img', 'desc_one', 'desc_two', 'priority')
    model.img_type = 'register'
    extra = 0
    max_num = 5
    verbose_name = u'新手注册流程'
    verbose_name_plural = u'新手注册流程'

    def get_queryset(self, request):
        return super(TemplatesRegisterInline, self).get_queryset(request).filter(img_type='register').order_by('-priority')


class ActivityTemplatesAdmin(admin.ModelAdmin):

    list_display = ('id', )
    inlines = [TemplatesImageInline, TemplatesRegisterInline]

    fieldsets = (
        ('logo', {'fields': ['logo', 'logo_other', 'location']}),
        ('banner', {'fields': ['banner']}),
        (u'活动描述', {'fields': ['desc', 'desc_time']}),
        (u'奖品图片和描述', {'fields': ['reward_img', 'reward_desc'], 'classes': ['collapse']}),
        (u'邀请好友', {'fields': ['introduce_img', 'introduce_desc'], 'classes': ['collapse']}),
        (u'规则描述', {'fields': ['rule_use', 'rule_activity', 'rule_reward'], 'classes': ['collapse']}),

    )


admin.site.register(ActivityTemplates, ActivityTemplatesAdmin)

admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityRule, ActivityRuleAdmin)
admin.site.register(ActivityRecord, ActivityRecordAdmin)