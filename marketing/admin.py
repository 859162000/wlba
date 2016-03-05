# -*- coding: utf-8 -*-

from django.contrib import admin
from marketing.models import Channels


class ChannelsAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("id", "code", "name", "description", "platform", "coop_status", "is_abandoned")
    search_fields = ("name",)
    list_filter = ("coop_status", "is_abandoned", "classification")

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Channels, ChannelsAdmin)
