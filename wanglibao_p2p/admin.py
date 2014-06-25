from django.contrib import admin
from models import P2PProduct, Warrant, WarrantCompany, P2PRecord, P2PEquity
from models import AmortizationRecord, ProductAmortization, EquityRecord


class UserEquityAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'equity', 'confirm', 'ratio', 'paid_principal', 'paid_interest', 'penal_interest')
    list_filter = ('confirm',)


class AmortizationInline(admin.TabularInline):
    model = ProductAmortization


class P2PProductAdmin(admin.ModelAdmin):
    inlines = [
        AmortizationInline
    ]

admin.site.register(P2PProduct, P2PProductAdmin)
admin.site.register(Warrant)
admin.site.register(P2PEquity, UserEquityAdmin)
admin.site.register(WarrantCompany)
admin.site.register(P2PRecord)
admin.site.register(AmortizationRecord)
admin.site.register(EquityRecord)