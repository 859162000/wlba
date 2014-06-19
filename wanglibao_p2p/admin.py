from django.contrib import admin
from models import P2PProduct, Warrant, UserEquity, WarrantCompany, P2PRecord, RecordCatalog
from models import P2PProductPayment, ProductUserAmortization, ProductAmortization,EquityRecord





class UserEquityAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'equity', 'confirm', 'ratio',)
    list_filter = ('confirm',)


admin.site.register(P2PProduct)
admin.site.register(Warrant)

admin.site.register(UserEquity, UserEquityAdmin)
admin.site.register(WarrantCompany)
admin.site.register(P2PRecord)
admin.site.register(RecordCatalog)
admin.site.register(P2PProductPayment)
admin.site.register(ProductAmortization)
admin.site.register(ProductUserAmortization)
admin.site.register(EquityRecord)