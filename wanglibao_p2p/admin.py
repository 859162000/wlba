from django.contrib import admin
from models import P2PProduct, Warrant, UserEquity, UserMargin, WarrantCompany, TradeRecord, TradeRecordType


admin.site.register(P2PProduct)
admin.site.register(Warrant)

admin.site.register(UserMargin)
admin.site.register(UserEquity)
admin.site.register(WarrantCompany)
admin.site.register(TradeRecord)
admin.site.register(TradeRecordType)