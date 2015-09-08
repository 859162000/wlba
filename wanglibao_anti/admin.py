from django.contrib import admin
from wanglibao_anti.models import AntiDelayCallback


class AntiDelayCallbackAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("channel", "status", "ip")
    search_fields = ()
    list_filter = ('status',)

admin.site.register(AntiDelayCallback, AntiDelayCallbackAdmin)
