from django.contrib import admin
from wanglibao_sms.models import PhoneValidateCode, ShortMessage


class PhoneValidateCodeAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'phone', 'validate_code', 'validate_type', 'is_validated', 'last_send_time')
    list_display_links = ('id',)
    search_fields = ('phone',)

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(PhoneValidateCode, PhoneValidateCodeAdmin)


class ShortMessageAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'phones', 'contents', 'type', 'status', 'created_at', 'context')
    list_display_links = ('id',)
    readonly_fields = ('status', 'context')
    search_fields = ('phones', 'contents')

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(ShortMessage, ShortMessageAdmin)
