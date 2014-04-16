from django.db import models
from django.contrib import admin
from django.forms import Textarea
from trust.models import Trust, Issuer


class TrustAdmin (admin.ModelAdmin):
    list_display = ('id', 'short_name', 'issuer', 'type')

admin.site.register(Trust, TrustAdmin)
admin.site.register(Issuer)