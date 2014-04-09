from django.contrib import admin
from wanglibao_hotlist.models import HotTrust, HotFinancing, HotFund


class HotTrustAdmin(admin.ModelAdmin):
    raw_id_fields = ('trust',)


class HotFinancingAdmin(admin.ModelAdmin):
    raw_id_fields = ('bank_financing',)


class HotFundAdmin(admin.ModelAdmin):
    raw_id_fields = ('fund',)

admin.site.register(HotTrust, HotTrustAdmin)
admin.site.register(HotFinancing, HotFinancingAdmin)
admin.site.register(HotFund, HotFundAdmin)
