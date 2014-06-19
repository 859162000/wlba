from django.contrib import admin

# Register your models here.
class UserMarginAdmin(admin.ModelAdmin):
    list_display = ('user', 'margin', 'freeze', 'withdrawing', )


class MarginRecordAdmin(admin.ModelAdmin):
    list_display = ('catalog', 'user', 'amount', 'description', 'checksum', 'trust')