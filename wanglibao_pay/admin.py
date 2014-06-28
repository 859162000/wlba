# -*- coding: utf-8 -*-
from django.contrib import admin

# Register your models here.
from wanglibao_pay.models import Bank, PayInfo, Card


class PayInfoAdmin(admin.ModelAdmin):
    list_display = ('get_phone', 'type', 'total_amount', 'fee', 'bank', 'card', 'status', 'create_time')
    search_fields = ['user__wanglibaouserprofile__phone', 'card__no']

    def get_phone(self, obj):
        return obj.user.wanglibaouserprofile.phone

    get_phone.short_description = u'手机'


class BankAdmin(admin.ModelAdmin):
    list_display = ('name', 'gate_id', 'code')


class CardAdmin(admin.ModelAdmin):
    list_display = ('get_phone', 'no', 'bank')
    search_fields = ['user__wanglibaouserprofile__phone', 'no']

    def get_phone(self, obj):
        return obj.user.wanglibaouserprofile.phone

    get_phone.short_description = u'手机'

admin.site.register(Bank, BankAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(PayInfo, PayInfoAdmin)
