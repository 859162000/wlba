from django.contrib import admin
from models import Order, OrderNote
# Register your models here.


class OrderAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'type', 'status', 'parent', 'created_at')
    raw_id_fields = ('parent', )
    search_fields = ('user__wanglibaouserprofile__phone',)
    list_filter = ('type', )

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


class OrderNoteAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'type', 'user', 'message', 'created_at', 'updated_at')
    raw_id_fields = ('user', 'order')
    search_fields = ('user__wanglibaouserprofile__phone',)
    list_filter = ('type', )

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderNote, OrderNoteAdmin)
