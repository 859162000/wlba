from django.contrib import admin
from models import Margin, MarginRecord
# Register your models here.
class UserMarginAdmin(admin.ModelAdmin):
    list_display = ('user', 'margin', 'freeze', 'withdrawing', )


class MarginRecordAdmin(admin.ModelAdmin):
    list_display = ('catalog', 'user', 'amount', 'description', )

admin.site.register(Margin, UserMarginAdmin)
admin.site.register(MarginRecord, MarginRecordAdmin)