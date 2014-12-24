from django.contrib import admin
from models import Order, OrderNote
# Register your models here.


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'status', 'parent', 'created_at')
    raw_id_fields = ('parent', )
    search_fields = ('user__wanglibaouserprofile__phone',)
    list_filter = ('type', )

class OrderNoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'user', 'message', 'created_at', 'updated_at')
    raw_id_fields = ('user', 'order')
    search_fields = ('user__wanglibaouserprofile__phone',)
    list_filter = ('type', )


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderNote, OrderNoteAdmin)
