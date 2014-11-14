#!/usr/bin/env python
# encoding:utf-8

import datetime
from django.contrib import admin
from misc.models import Misc

class MiscAdmin(admin.ModelAdmin):
    list_display = ("key", "value", "description", "format_created_at")

    def format_created_at(self, obj):
        return datetime.datetime.fromtimestamp(obj.created_at)
    format_created_at.short_description = u"创建时间"

admin.site.register(Misc, MiscAdmin)
