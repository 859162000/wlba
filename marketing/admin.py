from django.contrib import admin
from marketing.models import NewsAndReport, SiteData, PromotionToken


class NewsAndReportAdmin(admin.ModelAdmin):
    list_display = ("name", "link", "score")

admin.site.register(NewsAndReport, NewsAndReportAdmin)


class SiteDataAdmin(admin.ModelAdmin):
    list_display = ("id", "invest_threshold", "p2p_total_earning", "p2p_total_trade", "earning_rate", "highest_earning_rate", "demand_deposit_interest_rate", "one_year_interest_rate", "product_release_time")
    list_editable = ("invest_threshold", "p2p_total_earning", "p2p_total_trade", "earning_rate", "highest_earning_rate", "demand_deposit_interest_rate", "one_year_interest_rate", "product_release_time")
    list_display_link = ('id',)

admin.site.register(SiteData, SiteDataAdmin)


class PromotionTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "token")
    readonly_fields = ("user", "token")

admin.site.register(PromotionToken, PromotionTokenAdmin)
