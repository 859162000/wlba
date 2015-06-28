from django.contrib import admin
from models import FundHoldInfo, AvailableFund, TradeHistory, BindBank, MonetaryFundNetValue, DailyIncome, TradeInfo


class BindBankAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'no', 'user', 'bank_name', 'is_freeze', 'status', 'create_date')
    raw_id_fields = ('user', )
    search_fields = ('user__wanglibaouserprofile__phone', )
    list_filter = ('is_freeze', )

    def has_add_permission(self, request):
        return False


class DailyIncomeAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'user', 'income', 'date')
    raw_id_fields = ('user', )
    search_fields = ('user__wanglibaouserprofile__phone', )

    def has_add_permission(self, request):
        return False


class FundHoldInfoAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'user')
    search_fields = ('user__wanglibaouserprofile__phone', )
    raw_id_fields = ('user', )

    def has_add_permission(self, request):
        return False


class TradeHistoryAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'user')
    raw_id_fields = ('user', )
    search_fields = ('user__wanglibaouserprofile__phone', )

    def has_add_permission(self, request):
        return False


class TradeInfoAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'user')
    raw_id_fields = ('user', )
    search_fields = ('user__wanglibaouserprofile__phone', )

    def has_add_permission(self, request):
        return False


admin.site.register(TradeInfo, TradeInfoAdmin)
admin.site.register(FundHoldInfo, FundHoldInfoAdmin)
admin.site.register(AvailableFund)
admin.site.register(TradeHistory, TradeHistoryAdmin)
admin.site.register(BindBank, BindBankAdmin)
admin.site.register(MonetaryFundNetValue)
admin.site.register(DailyIncome, DailyIncomeAdmin)
