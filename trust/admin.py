from django.contrib import admin
from trust.models import Trust, Issuer


class TrustAdmin (admin.ModelAdmin):
    list_display = ('id', 'short_name', 'issuer', 'type')
    search_fields = ('short_name', 'issuer__name')

admin.site.register(Trust, TrustAdmin)
admin.site.register(Issuer)