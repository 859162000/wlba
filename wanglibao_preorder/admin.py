from django.contrib import admin
from wanglibao_preorder.models import PreOrder


class PreOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'phone', 'user_name', 'product_type', 'product_name', 'product_url', 'created_at')
    search_fields = ('user_name', 'phone')
    list_filter = ('status',)
    date_hierarchy = 'created_at'


admin.site.register(PreOrder, PreOrderAdmin)

