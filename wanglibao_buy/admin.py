from django.contrib import admin
from models import FundHoldInfo, AvailableFund, TradeHistory, BindBank, MonetaryFundNetValue, DailyIncome

# Register your models here.


class FundHoldInfoAdmin(admin.ModelAdmin):

    pass


class AvailableFundAdmin(admin.ModelAdmin):

    pass


class TradeHistoryAdmin(admin.ModelAdmin):

    pass


class BindBankAdmin(admin.ModelAdmin):

    pass


class MonetaryFundNetValueAdmin(admin.ModelAdmin):

    pass


class DailyIncomeAdmin(admin.ModelAdmin):

    pass


admin.site.register(FundHoldInfo, FundHoldInfoAdmin)
admin.site.register(AvailableFund, AvailableFundAdmin)
admin.site.register(TradeHistory, TradeHistoryAdmin)
admin.site.register(BindBank, BindBankAdmin)
admin.site.register(MonetaryFundNetValue, MonetaryFundNetValueAdmin)
admin.site.register(DailyIncome, DailyIncomeAdmin)
