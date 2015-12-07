# -*- coding: utf-8 -*-
from daterange_filter.filter import DateRangeFilter
from django.contrib import admin
from wanglibao_sms.models import PhoneValidateCode, ShortMessage, ArrivedRate, MessageTemplate


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


class ArrivedRateAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'channel', 'achieved', 'total_amount', 'rate', 'start', 'end', 'created_at')
    list_display_links = ('id',)
    readonly_fields = ('channel', 'achieved', 'total_amount', 'rate', 'start', 'end', 'created_at')
    search_fields = ('achieved', 'total_amount', 'rate', 'start', 'end')
    list_filter = (
        'channel',
        # ('created_at', DateFieldListFilter),  # 默认只有距离今天的天, 周, 月
        ('created_at', DateRangeFilter),
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return self.list_display + ('channel',)


class MessageTemplateAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'message_for', 'title', 'content', 'args_num', 'args_tips')
    list_display_links = ('id', 'message_for',)
    # readonly_fields = ('message_for',)
    search_fields = ('message_for', 'title', 'content', 'args_num')
    list_filter = (
        'message_for',
        'title',
        'content',
        'args_num',
    )

    def has_delete_permission(self, request, obj=None):
        return False

    # def has_add_permission(self, request):
    #     return False


admin.site.register(ShortMessage, ShortMessageAdmin)
admin.site.register(ArrivedRate, ArrivedRateAdmin)
admin.site.register(MessageTemplate, MessageTemplateAdmin)
# admin.site.register(MessageInRedis, MessageInRedisAdmin)
