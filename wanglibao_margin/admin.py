from django.contrib import admin
from models import Margin, MarginRecord


class UserMarginAdmin(admin.ModelAdmin):
    list_display = ('user', 'margin', 'freeze', 'withdrawing', )


class MarginRecordAdmin(admin.ModelAdmin):
    list_display = ('catalog', 'user', 'amount', 'description', 'margin_current')

admin.site.register(Margin, UserMarginAdmin)
admin.site.register(MarginRecord, MarginRecordAdmin)