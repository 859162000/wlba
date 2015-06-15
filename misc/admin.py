#!/usr/bin/env python
# encoding:utf-8

import datetime
from django.contrib import admin
from misc.models import Misc

class MiscAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("key", "value", "description", "format_created_at")

    def format_created_at(self, obj):
        return datetime.datetime.fromtimestamp(obj.created_at)
    format_created_at.short_description = u"创建时间"

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Misc, MiscAdmin)
