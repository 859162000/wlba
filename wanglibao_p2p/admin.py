from concurrency.admin import ConcurrentModelAdmin
from django.contrib import admin
from reversion.admin import VersionAdmin
from models import P2PProduct, Warrant, WarrantCompany, P2PRecord, P2PEquity, Attachment, ContractTemplate
from models import AmortizationRecord, ProductAmortization, EquityRecord, UserAmortization


class UserEquityAdmin(ConcurrentModelAdmin, VersionAdmin):
    list_display = ('user', 'product', 'equity', 'confirm', 'ratio', 'paid_principal', 'paid_interest', 'penal_interest')
    list_filter = ('confirm',)


class AmortizationInline(admin.TabularInline):
    model = ProductAmortization
    extra = 0
    exclude = ('version',)


class WarrantInline(admin.TabularInline):
    model = Warrant


class AttachementInline(admin.TabularInline):
    model = Attachment


class P2PEquityInline(admin.TabularInline):
    model = P2PEquity
    raw_id_fields = ('user',)
    readonly_fields = ('user', 'confirm', 'contract', 'equity', 'confirm_at')
    exclude = ('version',)
    extra = 0
    can_delete = False

    def get_queryset(self, request):
        return super(P2PEquityInline, self).get_queryset(request).select_related('user').select_related('user__wanglibaouserprofile')


class P2PProductAdmin(ConcurrentModelAdmin, VersionAdmin):
    inlines = [
        WarrantInline, AttachementInline, AmortizationInline, P2PEquityInline
    ]
    list_display = ('name', 'short_name', 'status', 'pay_method', 'end_time', 'audit_link')
    list_editable = ('status',)
    list_filter = ('status',)
    search_fields = ('name',)


class UserAmortizationAdmin(ConcurrentModelAdmin, VersionAdmin):
    list_display = ('product_amortization', 'user', 'principal', 'interest', 'penal_interest')


class P2PRecordAdmin(admin.ModelAdmin):
    list_display = ('catalog', 'order_id', 'product', 'user', 'amount', 'product_balance_after', 'create_time', 'description')


class WarrantAdmin(admin.ModelAdmin):
    list_display = ('product', 'name')


class AmortizationRecordAdmin(admin.ModelAdmin):
    list_display = ('catalog', 'order_id', 'amortization', 'user', 'term', 'principal', 'interest', 'penal_interest', 'description')


class EquityRecordAdmin(admin.ModelAdmin):
    list_display = ('catalog', 'order_id', 'product', 'user', 'amount', 'create_time', 'description')


admin.site.register(P2PProduct, P2PProductAdmin)
admin.site.register(Warrant, WarrantAdmin)
admin.site.register(P2PEquity, UserEquityAdmin)
admin.site.register(WarrantCompany)
admin.site.register(UserAmortization, UserAmortizationAdmin)
admin.site.register(ContractTemplate)
admin.site.register(P2PRecord, P2PRecordAdmin)
admin.site.register(EquityRecord, EquityRecordAdmin)
admin.site.register(AmortizationRecord, AmortizationRecordAdmin)
