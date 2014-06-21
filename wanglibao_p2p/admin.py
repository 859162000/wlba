from django.contrib import admin
from models import P2PProduct, Warrant, WarrantCompany, P2PRecord, UserAmortization, P2PEquity
from models import P2PProductPayment, AmortizationRecord, ProductAmortization,EquityRecord


class UserEquityAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'equity', 'confirm', 'ratio',)
    list_filter = ('confirm',)


admin.site.register(P2PProduct)
admin.site.register(Warrant)
admin.site.register(UserAmortization)
admin.site.register(P2PEquity, UserEquityAdmin)
admin.site.register(WarrantCompany)
admin.site.register(P2PRecord)
admin.site.register(P2PProductPayment)
admin.site.register(ProductAmortization)
admin.site.register(AmortizationRecord)
admin.site.register(EquityRecord)