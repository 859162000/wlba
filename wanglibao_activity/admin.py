# coding: utf-8

import time
import datetime
from django import forms
from django.contrib import admin
from django.utils import timezone
from django.db.models import Q
from import_export import resources, fields
from import_export.admin import ExportMixin
from django.contrib.admin import widgets
from models import Activity, ActivityRule, ActivityRecord, ActivityTemplates, \
    ActivityImages, WapActivityTemplates, ActivityShow, ActivityBannerPosition, ActivityBannerShow
import models as m


class ActivityAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('name', 'code', 'category', 'platform', 'product_cats', 'product_ids',
                    'channel', 'description', 'start_at', 'end_at',
                    'activity_status', 'is_stopped', 'priority')
    search_fields = ('name', 'channel')
    list_filter = ('category', 'platform', 'is_stopped')
    ordering = ('-priority', '-created_at')


class ActivityRuleAdmin(admin.ModelAdmin):
    list_display = ('activity', 'rule_name', 'rule_description', 'trigger_node', 'gift_type',
                    'redpack', 'reward', 'income', 'min_amount', 'max_amount', 'is_used')
    list_filter = ('trigger_node', 'gift_type', 'is_used')
    search_fields = ('rule_name', 'activity__name')


class CustomDateFilter(admin.SimpleListFilter):
    title = u'触发时间'
    parameter_name = u'trigger_at'

    def lookups(self, request, model_admin):
        return (
            ('today', u'今天'),
            ('yesterday', u'昨天'),
            ('before_yesterday', u'前天'),
            ('before_yesterday2', u'大前天')
        )

    def queryset(self, request, queryset):
        dt = datetime.datetime.now()
        if self.value() == 'today':
            return queryset.filter(trigger_at__gte=timezone.datetime(dt.year, dt.month, dt.day),
                                   trigger_at__lt=timezone.datetime(dt.year, dt.month, dt.day, 23, 59, 59))
        if self.value() == 'yesterday':
            ydt = dt - datetime.timedelta(days=1)
            return queryset.filter(trigger_at__gte=timezone.datetime(ydt.year, ydt.month, ydt.day),
                                   trigger_at__lt=timezone.datetime(ydt.year, ydt.month, ydt.day, 23, 59, 59))
        if self.value() == 'before_yesterday':
            bydt = dt - datetime.timedelta(days=2)
            return queryset.filter(trigger_at__gte=timezone.datetime(bydt.year, bydt.month, bydt.day),
                                   trigger_at__lt=timezone.datetime(bydt.year, bydt.month, bydt.day, 23, 59, 59))
        if self.value() == 'before_yesterday2':
            bydt2 = dt - datetime.timedelta(days=3)
            return queryset.filter(trigger_at__gte=timezone.datetime(bydt2.year, bydt2.month, bydt2.day),
                                   trigger_at__lt=timezone.datetime(bydt2.year, bydt2.month, bydt2.day, 23, 59, 59))


class ActivityResource(resources.ModelResource):
    activity = fields.Field(attribute="activity__name", column_name=u"活动名称")
    rule = fields.Field(attribute="rule__rule_name", column_name=u"规则名称")
    platform = fields.Field(attribute="platform", column_name=u"平台")
    trigger_node = fields.Field(attribute="trigger_node", column_name=u"触发节点")
    user = fields.Field(attribute="user__wanglibaouserprofile__phone", column_name=u"用户手机号")
    income = fields.Field(attribute="income", column_name=u"金额/收益")
    description = fields.Field(attribute="description", column_name=u"摘要详情")
    trigger_at = fields.Field(attribute="trigger_at", column_name=u"触发时间")

    class Meta:
        model = ActivityRecord
        fields = ('activity', 'rule', 'platform', 'trigger_node', 'gift_type',
                  'user', 'income', 'description', 'trigger_at')
        export_order = ('activity', 'rule', 'platform', 'trigger_node', 'gift_type',
                        'user', 'income', 'description', 'trigger_at')

    def dehydrate_platform(self, obj):
        return dict(m.PLATFORM)[obj.platform]

    def dehydrate_trigger_node(self, obj):
        return dict(m.TRIGGER_NODE)[obj.trigger_node]

    def dehydrate_trigger_at(self, obj):
        return timezone.localtime(obj.trigger_at).strftime("%Y-%m-%d %H:%M:%S")


class ActivityRecordAdmin(ExportMixin, admin.ModelAdmin):
    actions = None
    list_display = ('id', 'activity', 'rule', 'platform', 'trigger_node', 'msg_type',
                    'send_type', 'gift_type', 'description', 'user', 'income', 'trigger_at')
    list_filter = (
        'platform', 'trigger_node', 'msg_type', 'send_type', 'gift_type',
        CustomDateFilter
    )
    search_fields = ('activity__name', 'description', 'rule__rule_name', 'user__wanglibaouserprofile__phone')
    resource_class = ActivityResource

    def get_export_filename(self, file_format):
        date_str = timezone.now().strftime('%Y-%m-%d')
        filename = "%s-%s.%s" % (u"活动流水记录".encode('utf-8'),
                                 date_str,
                                 file_format.get_extension())
        return filename

    def __init__(self, *args, **kwargs):
        super(ActivityRecordAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

    def has_delete_permission(self, request, obj=None):
        return False


class ActivityImagesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'img_type', 'img', 'desc_one', 'desc_two')
    ordering = ('-id',)
    search_fields = ('name',)
    fieldsets = (
        (None, {'fields': ('img_type', 'name', 'img', 'desc_one', 'desc_two')}),
    )


class ActivityTemplatesForm(forms.ModelForm):
    class Meta:
        model = ActivityTemplates

    # def preview_link(self):
    #     # return u'<a href="/templates/zero/%s/" target="_blank">预览</a>' % str(self.id)
    #     return u'<a href="/templates/zero/" target="_blank">预览</a>'
    # preview_link.short_description = u'预览'
    # preview_link.allow_tags = True

    def clean(self):
        if self.cleaned_data.get('location'):
            if not (self.cleaned_data.get('logo', '') and self.cleaned_data.get('logo_other', '')):
                raise forms.ValidationError(u'当选择交换logo方式时，必须同时上传两个logo')

        # if self.cleaned_data.get('is_activity_desc') == 2:
        #     if not self.cleaned_data.get('desc'):
        #         raise forms.ValidationError(u'选择自定义设置方案时，必须填写“活动描述”')
        #     if not self.cleaned_data.get('desc_time'):
        #         raise forms.ValidationError(u'选择自定义设置方案时，必须填写“活动时间”')

        if self.cleaned_data.get('is_reward') == 3:
            if not self.cleaned_data.get('reward_img'):
                raise forms.ValidationError(u'选择自定义设置方案时，必须填写“活动奖品图片ID”')

        if self.cleaned_data.get('is_reward') == 4:
            if not self.cleaned_data.get('reward_img'):
                raise forms.ValidationError(u'选择自定义设置方案时，必须填写“活动奖品图片ID”')
            if not self.cleaned_data.get('reward_desc'):
                raise forms.ValidationError(u'选择自定义设置方案时，必须填写“奖品描述”')

        if self.cleaned_data.get('is_introduce') == 2:
            if not self.cleaned_data.get('introduce_img'):
                raise forms.ValidationError(u'选择自定义设置方案时，必须上传图片')

        if self.cleaned_data.get('is_teacher') == 3 and not self.cleaned_data.get('teacher_desc'):
            raise forms.ValidationError(u'选择自定义设置方案时，必须填写“新手投资模块描述”')

        # if self.cleaned_data.get('is_rule_use') == 2 and not self.cleaned_data.get('rule_use'):
        #     raise forms.ValidationError(u'选择自定义设置方案时，必须填写“使用规则”')
        #
        # if self.cleaned_data.get('is_rule_activity') == 2 and not self.cleaned_data.get('rule_activity'):
        #     raise forms.ValidationError(u'选择自定义设置方案时，必须填写“活动规则”')
        #
        # if self.cleaned_data.get('is_rule_reward') == 2 and not self.cleaned_data.get('rule_reward'):
        #     raise forms.ValidationError(u'选择自定义设置方案时，必须填写“奖品发放”')

        if self.cleaned_data.get('is_footer') == 2 and not self.cleaned_data.get('footer_color'):
            raise forms.ValidationError(u'选择自定义设置方案时，必须填写自定义底部背景颜色')

        if not self.cleaned_data.get('models_sequence'):
            raise forms.ValidationError(u'填写展示模块的顺序，创建模板时必须填写此项！')

        if self.cleaned_data.get('is_background') in (1, 2):
            if not self.cleaned_data.get('background_location'):
                raise forms.ValidationError(u'加载默认模块时，必须填写放置背景模块的序号')
            if self.cleaned_data.get('is_background') == 2 and not self.cleaned_data.get('background_img'):
                raise forms.ValidationError(u'自定义背景设置时，必须上传背景图片')

        if self.cleaned_data.get('is_login_href'):
            if not self.cleaned_data.get('login_href_desc'):
                raise forms.ValidationError(u'启用入口超链接时，必须填写入口超链接描述')
            if not self.cleaned_data.get('login_href'):
                raise forms.ValidationError(u'启用入口超链接时，必须填写入口超链接')

        return self.cleaned_data


class ActivityTemplatesAdmin(admin.ModelAdmin):
    form = ActivityTemplatesForm

    list_display = ('id', 'name', 'banner', 'preview_link')
    ordering = ('-id',)
    search_fields = ('name',)

    fieldsets = (
        (None, {'fields': ('name', )}),
        ('logo', {'fields': ('logo', 'logo_other', 'location')}),
        ('banner', {'fields': ('banner',)}),
        ('login', {'fields': ('is_login', 'login_desc', 'login_invite', 'is_login_href', 'login_href_desc', 'login_href')}),
        (u'底部背景颜色模块', {'fields': ('is_footer', 'footer_color')}),
        (u'1 活动时间及描述模块', {'fields': ('is_activity_desc', 'desc', 'desc_time', 'desc_img'), 'classes': ['collapse']}),
        (u'2 奖品图片和描述模块', {'fields': ('is_reward', 'reward_img', 'reward_desc'), 'classes': ['collapse']}),
        (u'3 邀请好友模块', {'fields': ['is_introduce', 'introduce_img'], 'classes': ['collapse']}),
        (u'4 新手投资模块', {'fields': ('is_teacher', 'teacher_desc'), 'classes': ['collapse']}),
        (u'5 使用规则模块', {'fields': ('is_rule_use', 'rule_use_name', 'rule_use'), 'classes': ['collapse']}),
        (u'6 活动规则模块', {'fields': ('is_rule_activity', 'rule_activity_name', 'rule_activity'), 'classes': ['collapse']}),
        (u'7 奖品发放规则模块', {'fields': ('is_rule_reward', 'rule_reward_name', 'rule_reward'), 'classes': ['collapse']}),
        (u'8 高收益柱形图介绍模块', {'fields': ('is_earning_one',), 'classes': ['collapse']}),
        (u'9 多种选择介绍模块', {'fields': ('is_earning_two',), 'classes': ['collapse']}),
        (u'10 活动投资奖励模块', {'fields': ('is_earning_three',), 'classes': ['collapse']}),
        (u'11 自定义图片或描述模块', {'fields': ('is_diy', 'diy_img', 'diy_location'), 'classes': ['collapse']}),
        (u'背景图片设置模块', {'fields': ('is_background', 'background_location', 'background_img')}),
        (u'模块展示顺序*', {'fields': ('models_sequence',)}),
    )


class WapActivityTemplatesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'url', 'aim_template', 'is_rendering', 'func_rendering', 'start_at', 'end_at', 'created_at', 'is_used')
    ordering = ('-id',)
    search_fields = ('name', 'url', 'aim_template')


class ActivityShowForm(forms.ModelForm):
    is_pc = forms.BooleanField(label=u'是否主站活动', required=False)
    is_app = forms.BooleanField(label=u'是否APP活动', required=False)
    pc_detail_link = forms.CharField(label=u'PC-活动详情页链接*', max_length=255, required=False)
    pc_template = forms.CharField(label=u'PC-活动详情页模板名称*', max_length=255, required=False)
    app_detail_link = forms.CharField(label=u'APP-活动详情页链接*', max_length=255, required=False)
    app_template = forms.CharField(label=u'APP-活动详情页模板名称*', max_length=255, required=False)
    start_at = forms.DateTimeField(label=u'活动页面展示开始时间*', widget=widgets.AdminSplitDateTime)
    end_at = forms.DateTimeField(label=u'活动页面展示结束时间*', widget=widgets.AdminSplitDateTime)

    def clean_pc_detail_link(self):
        is_pc = self.cleaned_data.get('is_pc')
        pc_detail_link = self.cleaned_data.get('pc_detail_link')

        if is_pc and not pc_detail_link:
            raise forms.ValidationError(u'这个字段是必须的')

        return pc_detail_link

    def clean_pc_template(self):
        is_pc = self.cleaned_data.get('is_pc')
        pc_template = self.cleaned_data.get('pc_template')

        if is_pc and not pc_template:
            raise forms.ValidationError(u'这个字段是必须的')

        return pc_template

    def clean_app_detail_link(self):
        is_app = self.cleaned_data.get('is_app')
        app_detail_link = self.cleaned_data.get('app_detail_link')

        if is_app and not app_detail_link:
            raise forms.ValidationError(u'这个字段是必须的')

        return app_detail_link

    def clean_app_template(self):
        is_app = self.cleaned_data.get('is_app')
        app_template = self.cleaned_data.get('app_template')

        if is_app and not app_template:
            raise forms.ValidationError(u'这个字段是必须的')

        return app_template

    def clean_start_at(self):
        start_at = self.cleaned_data.get('start_at')
        end_at = self.cleaned_data.get('end_at')
        if start_at and end_at:
            if start_at > end_at:
                raise forms.ValidationError(u'活动展示开始时间必须小于结束时间')

        return start_at

    def clean_end_at(self):
        start_at = self.cleaned_data.get('start_at')
        end_at = self.cleaned_data.get('end_at')
        if start_at and end_at:
            if start_at > end_at:
                raise forms.ValidationError(u'活动展示结束时间必须大于开始时间')

        return end_at

    class Meta:
        forms.model = ActivityShow


class ActivityShowAdmin(admin.ModelAdmin):
    actions = None
    search_fields = ('id', 'activity', 'channel')
    ordering = ('-priority', '-created_at')
    raw_id_fields = ('activity',)
    list_display = ('activity', 'activity_status', 'platform', 'priority')
    form = ActivityShowForm


class ActivityBannerPosForm(forms.ModelForm):
    queryset = ActivityShow.objects.filter(is_pc=True, link_is_hide=False)
    main = forms.ModelChoiceField(queryset=queryset, label=u'主推', required=True)
    second_left = forms.ModelChoiceField(queryset=queryset, label=u'副推左', required=True)
    second_right = forms.ModelChoiceField(queryset=queryset, label=u'副推右', required=True)

    def clean_main(self):
        main = self.cleaned_data.get('main')
        second_left = self.cleaned_data.get('second_left')
        second_right = self.cleaned_data.get('second_right')

        act_list = [second_left, second_right]
        if main in act_list:
            raise forms.ValidationError(u'活动不能重复')

        return main

    def clean_second_left(self):
        main = self.cleaned_data.get('main')
        second_left = self.cleaned_data.get('second_left')
        second_right = self.cleaned_data.get('second_right')

        act_list = [main, second_right]
        if second_left in act_list:
            raise forms.ValidationError(u'活动不能重复')

        return second_left

    def clean_second_right(self):
        main = self.cleaned_data.get('main')
        second_left = self.cleaned_data.get('second_left')
        second_right = self.cleaned_data.get('second_right')

        act_list = [main, second_left]
        if second_right in act_list:
            raise forms.ValidationError(u'活动不能重复')

        return second_right

    class Meta:
        forms.model = ActivityBannerPosition


class ActivityBannerPosAdmin(admin.ModelAdmin):
    actions = None
    search_fields = ('main', 'second_left', 'second_right')
    ordering = ('-priority', '-created_at',)
    form = ActivityBannerPosForm


class ActivityBannerShowForm(forms.ModelForm):
    queryset = ActivityShow.objects.filter(is_pc=True, link_is_hide=False)
    activity_show = forms.ModelChoiceField(queryset=queryset, label=u'活动展示')

    def clean(self):
        show_start_at = self.cleaned_data.get('show_start_at')
        show_end_at = self.cleaned_data.get('show_end_at')
        activity_show = self.cleaned_data.get('activity_show')
        banner_type = self.cleaned_data.get('banner_type')

        if not activity_show:
            raise forms.ValidationError(u'活动展示不能为空')

        if not show_start_at:
            raise forms.ValidationError(u'Banner展示开始时间不能为空')

        if not show_end_at:
            raise forms.ValidationError(u'Banner展示结束时间不能为空')

        if not banner_type:
            raise forms.ValidationError(u'Banner类型不能为空')

        if banner_type == u'主推':
            if not activity_show.main_banner:
                raise forms.ValidationError(u"所选『活动展示』未添加%sbanner" % banner_type)

        if banner_type == u'副推左':
            if not activity_show.left_banner:
                raise forms.ValidationError(u"所选『活动展示』未添加%sbanner" % banner_type)

        if banner_type == u'副推右':
            if not activity_show.right_banner:
                raise forms.ValidationError(u"所选『活动展示』未添加%sbanner" % banner_type)

        if show_start_at <= show_end_at:
            if activity_show.start_at <= show_start_at <= show_end_at <= activity_show.end_at:
                act_banner_shows = ActivityBannerShow.objects.filter(Q(show_start_at__lte=show_start_at,
                                                                       show_end_at__gte=show_start_at,
                                                                       banner_type=banner_type) |
                                                                     Q(show_start_at__lte=show_end_at,
                                                                       show_end_at__gte=show_end_at,
                                                                       banner_type=banner_type) |
                                                                     Q(show_start_at__gte=show_start_at,
                                                                       show_end_at__lte=show_end_at,
                                                                       banner_type=banner_type))
                this_id = self.instance.id
                for banner_show in act_banner_shows:
                    if this_id and this_id == banner_show.id:
                        continue
                    else:
                        raise forms.ValidationError(u"与活动banner展示(id为%s)展示时间冲突" % banner_show.id)
            else:
                raise forms.ValidationError(u"活动banner展示时间不在『活动展示』时间内")
        else:
            raise forms.ValidationError(u"banner展示开始时间不能大于banner展示结束时间")

        return self.cleaned_data

    class Meta:
        forms.model = ActivityBannerShow


class ActivityBannerShowAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'activity_show', 'banner_type', 'show_start_at', 'show_end_at', 'created_at')
    search_fields = ('id', 'activity_show', 'banner_type')
    ordering = ('show_start_at',)
    form = ActivityBannerShowForm


admin.site.register(WapActivityTemplates, WapActivityTemplatesAdmin)
admin.site.register(ActivityImages, ActivityImagesAdmin)
admin.site.register(ActivityTemplates, ActivityTemplatesAdmin)

admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityRule, ActivityRuleAdmin)
# admin.site.register(ActivityRecord, ActivityRecordAdmin)

admin.site.register(ActivityShow, ActivityShowAdmin)
admin.site.register(ActivityBannerPosition, ActivityBannerPosAdmin)
admin.site.register(ActivityBannerShow, ActivityBannerShowAdmin)
