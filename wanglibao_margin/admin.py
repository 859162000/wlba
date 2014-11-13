from django.contrib import admin
from models import Margin, MarginRecord


class UserMarginAdmin(admin.ModelAdmin):
    list_display = ('user', 'margin', 'freeze', 'withdrawing', )
    search_fields = ('user__wanglibaouserprofile__phone',)


class MarginRecordAdmin(admin.ModelAdmin):
    list_display = ('catalog', 'user', 'amount', 'description', 'margin_current')
    search_fields = ('user__wanglibaouserprofile__phone',)
    raw_id_fields = ('user', )

admin.site.register(Margin, UserMarginAdmin)
admin.site.register(MarginRecord, MarginRecordAdmin)