from django.contrib import admin
from models import Margin, MarginRecord


class UserMarginAdmin(admin.ModelAdmin):
    list_display = ('user', 'margin', 'freeze', 'withdrawing', )
    search_fields = ('user__wanglibaouserprofile__phone',)
    raw_id_fields = ('user', )
    readonly_fields = ('margin', 'freeze', 'withdrawing')


class MarginRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'catalog', 'user', 'amount', 'description', 'margin_current', 'create_time')
    search_fields = ('user__wanglibaouserprofile__phone',)
    raw_id_fields = ('user', )
    list_filter = ('catalog', )


admin.site.register(Margin, UserMarginAdmin)
admin.site.register(MarginRecord, MarginRecordAdmin)