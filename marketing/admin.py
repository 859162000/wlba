# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms
from django.utils import timezone

from views import AggregateView, MarketingView, TvView, TopsView, IntroducedAwardTemplate, YaoView
from play_list import InvestmentRewardView
from marketing.models import NewsAndReport, SiteData, PromotionToken, IntroducedBy, TimelySiteData, InviteCode, \
    Activity, ActivityRule, Reward, RewardRecord, Channels, ChannelsNew, IntroducedByReward, PlayList, \
    ActivityJoinLog, WanglibaoActivityReward, GiftOwnerGlobalInfo, GiftOwnerInfo, QuickApplyInfo, P2PReward, \
    P2PRewardRecord
from marketing.views import GennaeratorCode

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export import fields
from wanglibao.admin import ReadPermissionModelAdmin


class NewsAndReportAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "link", "score", "hits")


class SiteDataAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("id", "invest_threshold", "p2p_total_earning", "p2p_total_trade", "earning_rate", "highest_earning_rate", "demand_deposit_interest_rate", "one_year_interest_rate", "product_release_time")
    list_editable = ("invest_threshold", "p2p_total_earning", "p2p_total_trade", "earning_rate", "highest_earning_rate", "demand_deposit_interest_rate", "one_year_interest_rate", "product_release_time")
    list_display_link = ('id',)

    def has_delete_permission(self, request, obj=None):
        return False


class PromotionTokenAdmin(ReadPermissionModelAdmin):
    actions = None
    list_display = ("user", "token")
    search_fields = ['user__wanglibaouserprofile__phone', 'token']
    raw_id_fields = ('user', )

    def get_readonly_fields(self, request, obj=None):
        if not request.user.has_perm('marketing.view_promotiontoken'):
            return ("user", "token")
        return ()

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

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


class IntroducedByAdmin(ReadPermissionModelAdmin):
    actions = None
    list_display = ("id", "user", "introduced_by", "channel", "created_at", "bought_at", "gift_send_at")
    # list_editable = ("gift_send_at",)
    search_fields = ("user__wanglibaouserprofile__phone", "introduced_by__wanglibaouserprofile__phone")
    raw_id_fields = ('user', 'introduced_by', 'created_by')
    list_filter = ('channel__code', 'channel__name')
    resource_class = IntroducedByResource

    def get_queryset(self, request):
        qs = super(IntroducedByAdmin, self).get_queryset(request)
        qs = qs.select_related('user').select_related('user__wanglibaouserprofile')\
            .select_related('introduced_by').select_related('introduced_by__wanglibaouserprofile')
        return qs

    def get_readonly_fields(self, request, obj=None):
        # if not request.user.has_perm('marketing.view_introducedby'):
        #     return ("bought_at", "user", "introduced_by")
        return ("bought_at", "user", "introduced_by", 'created_by', 'channel', 'gift_send_at', 'product_id')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class TimelySitedataAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("created_at", "p2p_margin", "freeze_amount", "total_amount", "user_count")
    readonly_fields = ("p2p_margin", "freeze_amount", "total_amount", "user_count")

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class InviteCodeAdmin(ReadPermissionModelAdmin):
    actions = None
    list_display = ('id', 'code', 'is_used')
    list_filter = ('is_used',)
    search_fields = ['code']

    def get_readonly_fields(self, request, obj=None):
        """ 如果没有设置 view 权限，则返回字段为只读
        """
        # if not request.user.has_perm('marketing.view_invitecode'):
        #     return ('id', 'code', 'is_used')
        return ('code', 'is_used')

    def has_delete_permission(self, request, obj=None):
        return False


class ActivityAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'name', 'description')

    def has_delete_permission(self, request, obj=None):
        return False


class ActivityRuleAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'name', 'description', 'rule_type', 'rule_amount')

    def has_delete_permission(self, request, obj=None):
        return False


class RewardResource(resources.ModelResource):

    class Meta:
        model = Reward
        fields = ('id', 'type', 'content', 'description', 'is_used', 'end_time', 'create_time')

    def import_obj(self, instance, row, False):
        super(RewardResource, self).import_obj(instance, row, False)


class RewardAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    actions = None
    list_display = ('id', 'type', 'content', 'description', 'is_used', 'end_time', 'create_time')
    search_fields = ('type', 'content')
    list_filter = ('is_used', 'type')
    resource_class = RewardResource

    def has_delete_permission(self, request, obj=None):
        return False

class RewardRecordAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'user', 'reward', 'description', 'create_time')
    search_fields = ('user__wanglibaouserprofile__phone', 'description', "reward__type")
    raw_id_fields = ('user', 'reward')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return self.list_display


#class ClientDataAdmin(admin.ModelAdmin):
#    actions = None
#    list_display = ('id', 'version', 'userdevice', 'network', 'channelid', 'phone', 'action', 'create_time')
#    search_fields = ('phone', )
#    list_filter = ('network', 'action')
#
#    def has_delete_permission(self, request, obj=None):
#        return False
#
#    def has_add_permission(self, request):
#        return False
#
#    def get_readonly_fields(self, request, obj=None):
#        return self.list_display


class ChannelsAdmin(admin.ModelAdmin):
    actions = None
##    list_display = ("id", "code", "name", "description")
    list_display = ("id", "code", "name", "description", "platform", "coop_status", "is_abandoned")
    search_fields = ("name",)
##    list_filter = ("name",)
    list_filter = ("coop_status", "is_abandoned", "classification")

    # def __init__(self, *args, **kwargs):
    #     super(ChannelsAdmin, self).__init__(*args, **kwargs)
    #     self.list_display_links = (None, )

    def has_delete_permission(self, request, obj=None):
        return False


class IntroducedByRewardAdmin(admin.ModelAdmin):
    t = ('id', 'user', 'introduced_by_person', 'product', 'first_bought_at', 'first_amount', 'introduced_reward',
         'checked_status', 'checked_at', 'activity_start_at', 'activity_end_at', 'activity_amount_min', 'percent_reward',
         'user_send_status', 'user_send_amount', 'introduced_send_status', 'introduced_send_amount', )
    list_display = t
    raw_id_fields = ('user', 'introduced_by_person', 'product')
    fieldsets = [(None, {'fields': t},)]
    readonly_fields = t
    search_fields = ('user__wanglibaouserprofile__phone', 'introduced_by_person__wanglibaouserprofile__phone')
    ordering = ('id', 'created_at')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields

    def has_add_permission(self, request):
        return False


class PlayListAdmin(admin.ModelAdmin):
    list_display = ('id', 'play_at', 'user', 'amount', 'ranking', 'redpackevent', 'created_at', 'checked_status', 'reward')
    search_fields = ('user__wanglibaouserprofile__phone', 'redpackevent', )
    raw_id_fields = ('user', )


class ActivityJoinLogAdmin(admin.ModelAdmin):
    actions = None
    raw_id_fields = ('user',)
    list_display = ('id', 'user', 'action_type', 'gift_name', 'amount', 'action_message', 'join_times', 'create_time')
    search_fields = ('user', 'action_name')

    def get_readonly_fields(self, request, obj=None):
        return self.list_display

    def has_add_permission(self, request):
        return False


class WanglibaoActivityRewardAdmin(admin.ModelAdmin):
    """
       add by yihen@20150901
    """
    action = None
    list_display = ('user', 'total_chances', 'used_chances', 'total_awards', 'used_awards')
    readonly_fields = ('user', 'total_chances', 'total_awards', )


class ChannelsNewAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("id", "code", "name", "description", "coop_status")
    search_fields = ("name",)
    list_filter = ("name",)

    def has_delete_permission(self, request, obj=None):
        return False

class GiftOwnerGlobalInfoAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("description", "amount", "valid")


class GiftOwnerInfoAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("sender", "name", "phone", "address", "award", "type", "create_time", "update_time")
    readonly_fields = list_display

    def has_delete_permission(self, request, obj=None):
        return False


class QuickApplyInfoAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("name", "phone", "address", "apply_way", "apply_amount", "status", "create_time", "update_time")
    readonly_fields = list_display

    def has_delete_permission(self, request, obj=None):
        return None


class P2PRewardResource(resources.ModelResource):

    class Meta:
        model = Reward
        fields = ('id', 'type', 'channel', 'content', 'description', 'is_used', 'end_time', 'create_time')

    def import_obj(self, instance, row, False):
        super(P2PRewardResource, self).import_obj(instance, row, False)


class P2PRewardAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    actions = None
    list_display = ('id', 'type', 'channel', 'content', 'description', 'is_used', 'end_time', 'create_time')
    search_fields = ('type', 'content', 'channel')
    list_filter = ('is_used', 'type')
    raw_id_fields = ('channel',)
    resource_class = P2PRewardResource

    def has_delete_permission(self, request, obj=None):
        return False


class P2PRewardRecordAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'user', 'reward', 'order_id', 'description', 'create_time')
    search_fields = ('user__wanglibaouserprofile__phone', 'order_id', 'description', "reward__type")
    raw_id_fields = ('user', 'reward')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return self.list_display


admin.site.register(QuickApplyInfo, QuickApplyInfoAdmin) #add by Yihen@20151103
admin.site.register(GiftOwnerGlobalInfo, GiftOwnerGlobalInfoAdmin) #add by Yihen@20151103
admin.site.register(GiftOwnerInfo, GiftOwnerInfoAdmin) #add by Yihen@20151103
admin.site.register(WanglibaoActivityReward, WanglibaoActivityRewardAdmin)  # add by Yihen@20150901
admin.site.register(NewsAndReport, NewsAndReportAdmin)
admin.site.register(SiteData, SiteDataAdmin)
admin.site.register(PromotionToken, PromotionTokenAdmin)
admin.site.register(IntroducedBy, IntroducedByAdmin)
admin.site.register(TimelySiteData, TimelySitedataAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityRule, ActivityRuleAdmin)
admin.site.register(Reward, RewardAdmin)
admin.site.register(RewardRecord, RewardRecordAdmin)
admin.site.register(P2PReward, P2PRewardAdmin)
admin.site.register(P2PRewardRecord, P2PRewardRecordAdmin)
#admin.site.register(ClientData, ClientDataAdmin)
admin.site.register(Channels, ChannelsAdmin)
##admin.site.register(ChannelsNew, ChannelsNewAdmin)
admin.site.register(IntroducedByReward, IntroducedByRewardAdmin)
admin.site.register(ActivityJoinLog, ActivityJoinLogAdmin)
admin.site.register(PlayList, PlayListAdmin)

admin.site.register_view('statistics/diary', view=MarketingView.as_view(), name=u'日明细数据')
# admin.site.register_view('statistics/tops', view=TopsView.as_view(), name=u'日周月榜名单')
admin.site.register_view('statistics/tv', view=TvView.as_view(), name=u'统计数据汇总')
admin.site.register(InviteCode, InviteCodeAdmin)

admin.site.register_view('marketing/generatorcode', view=GennaeratorCode.as_view(),name=u'生成邀请码')


admin.site.register_view('statistics/aggregate', view=AggregateView.as_view(), name=u'累计购买金额统计单')
# 停止邀请收益统计使用
# admin.site.register_view('statistics/introduced_by', view=IntroducedAwardTemplate.as_view(), name=u'邀请收益统计')
admin.site.register_view('statistics/investment_reward', view=InvestmentRewardView.as_view(), name=u'打榜统计发红包')
