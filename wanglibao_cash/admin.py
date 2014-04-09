from django.contrib import admin
from wanglibao_cash.models import Cash, CashIssuer


class CashAdmin(admin.ModelAdmin):
    list_display = ('name', 'profit_rate_7days', 'profit_10000')

admin.site.register(Cash, CashAdmin)
admin.site.register(CashIssuer)
