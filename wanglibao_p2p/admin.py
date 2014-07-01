from django.contrib import admin
from models import P2PProduct, Warrant, WarrantCompany, P2PRecord, P2PEquity, Attachment, ContractTemplate
from models import AmortizationRecord, ProductAmortization, EquityRecord, UserAmortization


class UserEquityAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'equity', 'confirm', 'ratio', 'paid_principal', 'paid_interest', 'penal_interest')
    list_filter = ('confirm',)


class AmortizationInline(admin.TabularInline):
    model = ProductAmortization


class WarrantInline(admin.TabularInline):
    model = Warrant


class AttachementInline(admin.TabularInline):
    model = Attachment


class P2PProductAdmin(admin.ModelAdmin):
    inlines = [
        WarrantInline, AttachementInline, AmortizationInline
    ]
    list_display = ('name', 'short_name', 'status', 'pay_method', 'end_time', 'closed')


class UserAmortizationAdmin(admin.ModelAdmin):
    list_display = ('product_amortization', 'user', 'principal', 'interest', 'penal_interest')

admin.site.register(P2PProduct, P2PProductAdmin)
admin.site.register(Warrant)
admin.site.register(P2PEquity, UserEquityAdmin)
admin.site.register(WarrantCompany)
admin.site.register(P2PRecord)
admin.site.register(AmortizationRecord)
admin.site.register(EquityRecord)
admin.site.register(UserAmortization, UserAmortizationAdmin)
admin.site.register(ContractTemplate)
