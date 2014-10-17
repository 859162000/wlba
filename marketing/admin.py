# -*- coding: utf-8 -*-

from django.contrib import admin
from views import MarketingView

from marketing.models import NewsAndReport, SiteData, PromotionToken, IntroducedBy, TimelySiteData, InviteCode
from marketing.views import GennaeratorCode

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export import fields


class NewsAndReportAdmin(admin.ModelAdmin):
    list_display = ("name", "link", "score")


class SiteDataAdmin(admin.ModelAdmin):
    list_display = ("id", "invest_threshold", "p2p_total_earning", "p2p_total_trade", "earning_rate", "highest_earning_rate", "demand_deposit_interest_rate", "one_year_interest_rate", "product_release_time")
    list_editable = ("invest_threshold", "p2p_total_earning", "p2p_total_trade", "earning_rate", "highest_earning_rate", "demand_deposit_interest_rate", "one_year_interest_rate", "product_release_time")
    list_display_link = ('id',)


class PromotionTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token")
    #readonly_fields = ("user", "token")

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


class IntroducedByAdmin(ImportExportModelAdmin):
    list_display = ("id", "user", "introduced_by", "created_at", "bought_at", "gift_send_at")
    readonly_fields = ("bought_at", "user", "introduced_by")
    list_editable = ("gift_send_at",)

    resource_class = IntroducedByResource

    def get_queryset(self, request):
        qs = super(IntroducedByAdmin, self).get_queryset(request)
        qs = qs.select_related('user').select_related('user__wanglibaouserprofile')\
            .select_related('introduced_by').select_related('introduced_by__wanglibaouserprofile')
        return qs


class TimelySitedataAdmin(admin.ModelAdmin):
    list_display = ("created_at", "p2p_margin", "freeze_amount", "total_amount", "user_count")
    readonly_fields = ("p2p_margin", "freeze_amount", "total_amount", "user_count")


class InviteCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'is_used')
    readonly_fields = ('code', )

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(NewsAndReport, NewsAndReportAdmin)
admin.site.register(SiteData, SiteDataAdmin)
admin.site.register(PromotionToken, PromotionTokenAdmin)
admin.site.register(IntroducedBy, IntroducedByAdmin)
admin.site.register(TimelySiteData, TimelySitedataAdmin)

admin.site.register_view('statistics/diary', view=MarketingView.as_view(),name=u'diary')
admin.site.register(InviteCode, InviteCodeAdmin)

admin.site.register_view('marketing/generatorcode', view=GennaeratorCode.as_view(),name=u'生成邀请码')
