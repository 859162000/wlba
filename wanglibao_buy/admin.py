from django.contrib import admin
from models import FundHoldInfo, AvailableFund, TradeHistory, BindBank, MonetaryFundNetValue, DailyIncome, TradeInfo


admin.site.register(TradeInfo)
admin.site.register(FundHoldInfo)
admin.site.register(AvailableFund)
admin.site.register(TradeHistory)
admin.site.register(BindBank)
admin.site.register(MonetaryFundNetValue)
admin.site.register(DailyIncome)
