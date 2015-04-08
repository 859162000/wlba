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
    actions = None
    list_display = ('id', 'activity', 'rule', 'platform', 'trigger_node', 'msg_type', \
                    'send_type', 'description', 'user', 'income', 'trigger_at')
    list_filter = ('platform', 'trigger_node', 'msg_type', 'send_type',)
    search_fields = ('activity__name', 'rule__rule_name', 'user__wanglibaouserprofile__phone')

    def __init__(self, *args, **kwargs):
        super(ActivityRecordAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ActivityImagesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'img_type', 'img', 'desc_one', 'desc_two', 'priority')

    ordering = ('id', '-img_type', '-priority')


class ActivityTemplatesForm(forms.ModelForm):
    class Meta:
        model = ActivityTemplates

    def clean(self):
        if self.cleaned_data.get('location'):
            if not (self.cleaned_data.get('logo', '') and self.cleaned_data.get('logo_other', '')):
                raise forms.ValidationError(u'当选择交换logo方式时，必须同时上传两个logo')

        if self.cleaned_data.get('is_activity_desc') == 2:
            if not self.cleaned_data.get('desc'):
                raise forms.ValidationError(u'选择自定义设置方案时，必须填写“活动描述”')
            if not self.cleaned_data.get('desc_time'):
                raise forms.ValidationError(u'选择自定义设置方案时，必须填写“活动时间”')

        if self.cleaned_data.get('is_reward') == 2:
            if not self.cleaned_data.get('reward_img'):
                raise forms.ValidationError(u'选择自定义设置方案时，必须填写“活动奖品图片ID”')
            if not self.cleaned_data.get('reward_desc'):
                raise forms.ValidationError(u'选择自定义设置方案时，必须填写“奖品描述”')

        if self.cleaned_data.get('is_introduce') == 2:
            # if not self.introduce_desc:
            #     raise ValidationError(u'选择自定义设置方案时，必须填写“邀请好友描述”')
            if not self.cleaned_data.get('introduce_img'):
                raise forms.ValidationError(u'选择自定义设置方案时，必须填写“邀请好友指定图片ID”')
        if self.cleaned_data.get('is_teacher') == 2 and not self.cleaned_data.get('teacher_desc'):
            raise forms.ValidationError(u'选择自定义设置方案时，必须填写“新手投资模块描述”')

        if self.cleaned_data.get('is_rule_use') == 2 and not self.cleaned_data.get('rule_use'):
            raise forms.ValidationError(u'选择自定义设置方案时，必须填写“使用规则”')

        if self.cleaned_data.get('is_rule_activity') == 2 and not self.cleaned_data.get('rule_activity'):
            raise forms.ValidationError(u'选择自定义设置方案时，必须填写“活动规则”')

        if self.cleaned_data.get('is_rule_reward') == 2 and not self.cleaned_data.get('rule_reward'):
            raise forms.ValidationError(u'选择自定义设置方案时，必须填写“奖品发放”')

        if self.cleaned_data.get('is_footer') == 2 and not self.cleaned_data.get('footer_color'):
            raise forms.ValidationError(u'选择自定义设置方案时，必须填写自定义底部背景颜色')

        return self.cleaned_data


class ActivityTemplatesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'banner')

    ordering = ('id',)

    form = ActivityTemplatesForm

    fieldsets = (
        (None, {'fields': ('name', )}),
        ('logo', {'fields': ('logo', 'logo_other', 'location')}),
        ('banner and login', {'fields': ('banner', 'is_login', 'login_desc')}),
        (u'活动时间及描述模块', {'fields': ('is_activity_desc', 'desc', 'desc_time', 'desc_img'), 'classes': ['collapse']}),
        (u'奖品图片和描述模块', {'fields': ('is_reward', 'reward_img', 'reward_desc'), 'classes': ['collapse']}),
        (u'邀请好友模块', {'fields': ['is_introduce', 'introduce_img'], 'classes': ['collapse']}),
        (u'新手投资模块', {'fields': ('is_teacher', 'teacher_desc'), 'classes': ['collapse']}),
        (u'使用规则模块', {'fields': ('is_rule_use', 'rule_use'), 'classes': ['collapse']}),
        (u'活动规则模块', {'fields': ('is_rule_activity', 'rule_activity'), 'classes': ['collapse']}),
        (u'奖品发放规则模块', {'fields': ('is_rule_reward', 'rule_reward'), 'classes': ['collapse']}),
        (u'底部背景颜色模块', {'fields': ('is_footer', 'footer_color'), 'classes': ['collapse']}),
    )


admin.site.register(ActivityImages, ActivityImagesAdmin)
admin.site.register(ActivityTemplates, ActivityTemplatesAdmin)

admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityRule, ActivityRuleAdmin)
admin.site.register(ActivityRecord, ActivityRecordAdmin)