from django.contrib import admin
from wanglibao_sms.models import PhoneValidateCode, ShortMessage


class PhoneValidateCodeAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'phone', 'validate_code', 'validate_type', 'is_validated', 'last_send_time')
    list_display_links = ('id',)
    search_fields = ('phone',)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        # return [f.name for f in self.model._meta.fields]
        return self.list_display + ('data',)

admin.site.register(PhoneValidateCode, PhoneValidateCodeAdmin)


class ShortMessageAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'phones', 'contents', 'type', 'status', 'created_at', 'context')
    list_display_links = ('id',)
    readonly_fields = ('status', 'context')
    # Modify by hb on 2015-10-09 : remove search for "contents"
    #search_fields = ('phones', 'contents')
    search_fields = ('=phones', )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return self.list_display + ('channel',)

admin.site.register(ShortMessage, ShortMessageAdmin)
