from django.contrib import admin
from models import Order, OrderNote
# Register your models here.


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'status', 'parent', 'created_at')
    raw_id_fields = ('parent', )

class OrderNoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'user', 'message', 'created_at', 'updated_at')
    raw_id_fields = ('user', 'order')

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderNote, OrderNoteAdmin)
