from django.contrib import admin
from models import FundHoldInfo

# Register your models here.


class FundHoldInfoAdmin(admin.ModelAdmin):

    pass


admin.site.register(FundHoldInfo, FundHoldInfoAdmin)
