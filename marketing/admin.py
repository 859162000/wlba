# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils import timezone
from views import AggregateView, MarketingView, TvView, TopsView

from marketing.models import NewsAndReport, SiteData, PromotionToken, IntroducedBy, TimelySiteData, InviteCode, \
    Activity, ActivityRule, Reward, RewardRecord, ClientData
from marketing.views import GennaeratorCode

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export import fields
from wanglibao.admin import ReadPermissionModelAdmin


class NewsAndReportAdmin(admin.ModelAdmin):
    list_display = ("name", "link", "score")


class SiteDataAdmin(admin.ModelAdmin):
    list_display = ("id", "invest_threshold", "p2p_total_earning", "p2p_total_trade", "earning_rate", "highest_earning_rate", "demand_deposit_interest_rate", "one_year_interest_rate", "product_release_time")
    list_editable = ("invest_threshold", "p2p_total_earning", "p2p_total_trade", "earning_rate", "highest_earning_rate", "demand_deposit_interest_rate", "one_year_interest_rate", "product_release_time")
    list_display_link = ('id',)


class PromotionTokenAdmin(ReadPermissionModelAdmin):
    list_display = ("user", "token")
    search_fields = ['user__wanglibaouserprofile__phone']
    raw_id_fields = ('user', )

    def get_readonly_fields(self, request, obj=None):
        if not request.user.has_perm('marketing.view_promotiontoken'):
            return ("user", "token")
        return ()

class IntroducedByResource(resources.ModelResource):

    user_name = fields.Field(attribute="user__wanglibaouserprofile__name")
    user_phone = fields.Field(attribute="user__wanglibaouserprofile__phone")
    introduced_name = fields.Field(attribute="introduced_by__wanglibaouserprofile__name")
    introduced_phone = fields.Field(attribute="introduced_by__wanglibaouserprofile__phone")
    chanel = fields.Field(attribute="introduced_by__username")

    class Meta:
        model = IntroducedBy
        fields = ('user_name', 'user_phone','introduce_name', 'introduce_phone', 'chanel',
                  'created_at', 'bought_at', 'gift_send_at' )

    def dehydrate_created_at(self, obj):
        return timezone.localtime(obj.created_at).strftime("%Y-%m-%d %H:%M:%S")

    def dehydrate_bought_at(self, obj):
        if obj.bought_at:
            return timezone.localtime(obj.bought_at).strftime("%Y-%m-%d %H:%M:%S")

    def dehydrate_gift_send_at(self, obj):
        if obj.gift_send_at:
            return timezone.localtime(obj.gift_send_at).strftime("%Y-%m-%d %H:%M:%S")


class IntroducedByAdmin(ReadPermissionModelAdmin, ImportExportModelAdmin):
    list_display = ("id", "user", "introduced_by", "created_at", "bought_at", "gift_send_at")
    list_editable = ("gift_send_at",)
    search_fields = ("user__wanglibaouserprofile__phone", "introduced_by__wanglibaouserprofile__phone")
    raw_id_fields = ('user', 'introduced_by', 'created_by')
    resource_class = IntroducedByResource

    def get_queryset(self, request):
        qs = super(IntroducedByAdmin, self).get_queryset(request)
        qs = qs.select_related('user').select_related('user__wanglibaouserprofile')\
            .select_related('introduced_by').select_related('introduced_by__wanglibaouserprofile')
        return qs

    def get_readonly_fields(self, request, obj=None):
        if not request.user.has_perm('marketing.view_introducedby'):
            return ("bought_at", "user", "introduced_by")
        return ()

class TimelySitedataAdmin(admin.ModelAdmin):
    list_display = ("created_at", "p2p_margin", "freeze_amount", "total_amount", "user_count")
    readonly_fields = ("p2p_margin", "freeze_amount", "total_amount", "user_count")


class InviteCodeAdmin(ReadPermissionModelAdmin):
    list_display = ('id', 'code', 'is_used')
    search_fields = ['code']

    def get_readonly_fields(self, request, obj=None):
        """ 如果没有设置 view 权限，则返回字段为只读
        """
        if not request.user.has_perm('marketing.view_invitecode'):
            return ('id', 'code', 'is_used')
        return ()


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')


class ActivityRuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'rule_type', 'rule_amount')


class RewardResource(resources.ModelResource):

    class Meta:
        model = Reward
        fields = ('id', 'type', 'content', 'description', 'is_used', 'end_time', 'create_time')

    def import_obj(self, instance, row, False):
        super(RewardResource, self).import_obj(instance, row, False)


class RewardAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'type', 'content', 'description', 'is_used', 'end_time', 'create_time')
    search_fields = ('type', 'content')
    list_filter = ('is_used', 'type')
    resource_class = RewardResource

class RewardRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'reward', 'description', 'create_time')
    search_fields = ('user__wanglibaouserprofile__phone', 'description', "reward__type")
    raw_id_fields = ('user', 'reward')

class ClientDataAdmin(admin.ModelAdmin):

    list_display = ('id', 'version', 'userdevice', 'network', 'channelid', 'phone', 'action', 'create_time')
    search_fields = ('phone', )
    list_filter = ('network', 'action')


admin.site.register(NewsAndReport, NewsAndReportAdmin)
admin.site.register(SiteData, SiteDataAdmin)
admin.site.register(PromotionToken, PromotionTokenAdmin)
admin.site.register(IntroducedBy, IntroducedByAdmin)
admin.site.register(TimelySiteData, TimelySitedataAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityRule, ActivityRuleAdmin)
admin.site.register(Reward, RewardAdmin)
admin.site.register(RewardRecord, RewardRecordAdmin)
admin.site.register(ClientData, ClientDataAdmin)

admin.site.register_view('statistics/diary', view=MarketingView.as_view(), name=u'日明细数据')
admin.site.register_view('statistics/tops', view=TopsView.as_view(), name=u'日周月榜名单')
admin.site.register_view('statistics/tv', view=TvView.as_view(), name=u'统计数据汇总')
admin.site.register(InviteCode, InviteCodeAdmin)

admin.site.register_view('marketing/generatorcode', view=GennaeratorCode.as_view(),name=u'生成邀请码')


admin.site.register_view('statistics/aggregate', view=AggregateView.as_view(), name=u'累计购买金额统计单')

