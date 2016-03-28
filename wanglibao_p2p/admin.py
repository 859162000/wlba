# coding=utf-8

from django.contrib import admin
from .models import P2PProduct


class P2PProductAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'name', 'total_amount', 'types', 'brief', 'status')
    search_fields = ('id', 'name')
    from_encoding = 'utf-8'

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(P2PProduct, P2PProductAdmin)
