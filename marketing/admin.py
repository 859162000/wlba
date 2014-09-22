from django.contrib import admin
from marketing.models import NewsAndReport, SiteData, PromotionToken, IntroducedBy, TimelySiteData


class NewsAndReportAdmin(admin.ModelAdmin):
    list_display = ("name", "link", "score")


class SiteDataAdmin(admin.ModelAdmin):
    list_display = ("id", "invest_threshold", "p2p_total_earning", "p2p_total_trade", "earning_rate", "highest_earning_rate", "demand_deposit_interest_rate", "one_year_interest_rate", "product_release_time")
    list_editable = ("invest_threshold", "p2p_total_earning", "p2p_total_trade", "earning_rate", "highest_earning_rate", "demand_deposit_interest_rate", "one_year_interest_rate", "product_release_time")
    list_display_link = ('id',)


class PromotionTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token")
    readonly_fields = ("user", "token")


class IntroducedByAdmin(admin.ModelAdmin):
    list_display = ("user", "introduced_by", "created_at", "bought_at", "gift_send_at")
    readonly_fields = ("bought_at", "user", "introduced_by")
    list_editable = ("gift_send_at",)

    def get_queryset(self, request):
        qs = super(IntroducedByAdmin, self).get_queryset(request)
        qs = qs.select_related('user').select_related('user__wanglibaouserprofile')\
            .select_related('introduced_by').select_related('introduced_by__wanglibaouserprofile')
        return qs


class TimelySitedataAdmin(admin.ModelAdmin):
    list_display = ("created_at", "p2p_margin", "freeze_amount", "total_amount", "user_count")
    readonly_fields = ("p2p_margin", "freeze_amount", "total_amount", "user_count")

admin.site.register(NewsAndReport, NewsAndReportAdmin)
admin.site.register(SiteData, SiteDataAdmin)
admin.site.register(PromotionToken, PromotionTokenAdmin)
admin.site.register(IntroducedBy, IntroducedByAdmin)
admin.site.register(TimelySiteData, TimelySitedataAdmin)
