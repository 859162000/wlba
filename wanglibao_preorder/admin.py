from django.contrib import admin
from wanglibao_preorder.models import PreOrder


class PreOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'phone', 'user_name', 'product_type', 'amount', 'product_name', 'product_url', 'created_at')
    search_fields = ('user_name', 'phone', 'product_type', 'product_name')
    list_filter = ('status',)
    raw_id_fields = ('user', )


admin.site.register(PreOrder, PreOrderAdmin)

