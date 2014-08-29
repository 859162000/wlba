# -*- coding: utf-8 -*-
from django.contrib import admin

# Register your models here.
from wanglibao_pay.models import Bank, PayInfo, Card
from wanglibao_pay.views import WithdrawTransactions, WithdrawRollback, WithdrawRechargeRecord, \
    AdminTransactionWithdraw, AdminTransactionDeposit


class PayInfoAdmin(admin.ModelAdmin):
    list_display = ('get_phone', 'type', 'total_amount', 'fee', 'bank', 'card_no', 'status', 'create_time')
    search_fields = ['user__wanglibaouserprofile__phone', 'card__no']
    raw_id_fields = ('order', 'margin_record')

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


admin.site.register_view('pay/withdraw/audit', view=WithdrawTransactions.as_view(), name=u'提现申请审核页面')
admin.site.register_view('pay/withdraw/rollback', view=WithdrawRollback.as_view(), name=u'提现申请失败回滚页面')
admin.site.register_view('pay/withdraw/recharge_record', view=WithdrawRechargeRecord.as_view(), name=u'用户充值记录详情')

admin.site.register_view('pay/transaction/withdraw', view=AdminTransactionWithdraw.as_view(), name=u'交易记录详情')
admin.site.register_view('pay/transaction/deposit', view=AdminTransactionDeposit.as_view(), name=u'交易记录详情')

