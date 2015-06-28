from django.contrib import admin
from models import Margin, MarginRecord


class UserMarginAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('user', 'margin', 'freeze', 'withdrawing', )
    search_fields = ('user__wanglibaouserprofile__phone',)
    raw_id_fields = ('user', )
    readonly_fields = ('margin', 'freeze', 'withdrawing')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return ('user', 'margin', 'freeze', 'withdrawing', 'invest')


class MarginRecordAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'order_id', 'catalog', 'user', 'amount', 'description', 'margin_current', 'create_time')
    search_fields = ('user__wanglibaouserprofile__phone',)
    raw_id_fields = ('user', )
    list_filter = ('catalog', )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return self.list_display


admin.site.register(Margin, UserMarginAdmin)
admin.site.register(MarginRecord, MarginRecordAdmin)