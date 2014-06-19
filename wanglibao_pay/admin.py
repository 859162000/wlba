from django.contrib import admin

# Register your models here.
from wanglibao_pay.models import Bank, PayInfo, Card

admin.site.register(Bank)
admin.site.register(Card)
admin.site.register(PayInfo)
