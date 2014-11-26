# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils import timezone
# Register your models here.
from wanglibao_pay.models import Bank, PayInfo, Card
from wanglibao_pay.views import WithdrawTransactions, WithdrawRollback, \
    AdminTransaction


class PayInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_phone', 'get_name', 'type', 'total_amount', 'fee', 'bank', 'card_no', 'status', 'create_time', 'update_time', 'error_message')
    search_fields = ['=user__wanglibaouserprofile__phone', '=id']
    raw_id_fields = ('order', 'margin_record', "user")
    list_filter = ('status', )

    def get_phone(self, obj):
        return obj.user.wanglibaouserprofile.phone

    get_phone.short_description = u'手机'

    def get_name(self, obj):
        return obj.user.wanglibaouserprofile.name
    get_name.short_description = u'姓名'


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


admin.site.register_view('pay/withdraw/audit', view=WithdrawTransactions.as_view(), name=u'提现申请审核页面')
admin.site.register_view('pay/withdraw/rollback', view=WithdrawRollback.as_view(), name=u'提现申请失败回滚页面')

admin.site.register_view('pay/transaction', view=AdminTransaction.as_view(),name=u'交易记录详情')


