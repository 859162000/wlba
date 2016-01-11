#!/usr/bin/env python
# encoding:utf-8

from django.contrib import admin

from experience_gold import models


class ExperienceProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'period', 'expected_earning_rate', 'isvalid', 'description')

    def has_delete_permission(self, request, obj=None):
        return False


class ExperienceEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'amount', 'give_mode', 'give_platform', 'target_channel',
                    'available_at', 'unavailable_at', 'invalid')
    search_fields = ('name', )

    def has_delete_permission(self, request, obj=None):
        return False


class ExperienceEventRecordAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'event', 'user', 'apply_platform', 'apply_at', 'apply_amount', 'created_at')
    search_fields = ('=user__wanglibaouserprofile__phone', )
    raw_id_fields = ('user', )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


class ExperienceAmortizationAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'product', 'user', 'term', 'term_date', 'principal', 'interest',
                    'settled', 'settlement_time', 'created_time')
    raw_id_fields = ('user', )
    search_fields = ('=user__wanglibaouserprofile__phone', )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


admin.site.register(models.ExperienceProduct, ExperienceProductAdmin)
admin.site.register(models.ExperienceEvent, ExperienceEventAdmin)
admin.site.register(models.ExperienceEventRecord, ExperienceEventRecordAdmin)
admin.site.register(models.ExperienceAmortization, ExperienceAmortizationAdmin)
