# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils import timezone
# Register your models here.
from wanglibao_pay.models import Bank, PayInfo, Card, WithdrawCard, WithdrawCardRecord, WhiteListCard, BlackListCard
from wanglibao_pay.views import WithdrawTransactions, WithdrawRollback, \
    AdminTransaction
# , 'channel', 'type'


class PayInfoStatusFilter(admin.SimpleListFilter):
    title = u'状态'
    parameter_name = u'status'

    def lookups(self, request, model_admin):
        return (
            (u'处理中', u'处理中'),
            (u'失败', u'失败'),
            (u'已受理', u'已受理'),
            (u'异常', u'异常'),
            (u'成功', u'成功')
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status__exact=self.value())
        else:
            return queryset


class PayInfoChannelFilter(admin.SimpleListFilter):
    title = u'支付渠道'
    parameter_name = u'channel'

    def lookups(self, request, model_admin):
        return (
            (u'huifu', u'huifu'),
            (u'huifu_bind', u'huifu_bind'),
            (u'yeepay', u'yeepay'),
            (u'yeepay_bind', u'yeepay_bind'),
            (u'app', u'app'),
            (u'kuaipay', u'kuaipay')
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(channel__exact=self.value())
        else:
            return queryset


class PayInfoTypeFilter(admin.SimpleListFilter):
    title = u'支付类型'
    parameter_name = u'type'

    def lookups(self, request, model_admin):
        return (
            (u'D', u'充值'),
            (u'W', u'提现'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(type__exact=self.value())
        else:
            return queryset


class PayInfoAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'get_phone', 'get_name', 'type', 'total_amount', 'fee', 'management_fee', 'bank', 'card_no', 'status', 'create_time', 'update_time', 'error_message', 'channel')
    # Modify by hb on 2015-10-23
    #search_fields = ['=user__wanglibaouserprofile__phone', '=id']
    search_fields = ['=user__wanglibaouserprofile__phone']
    raw_id_fields = ('order', 'margin_record', "user")
    list_filter = (
        PayInfoStatusFilter, PayInfoChannelFilter, PayInfoTypeFilter
    )
    list_per_page = 100

    def get_phone(self, obj):
        return obj.user.wanglibaouserprofile.phone

    get_phone.short_description = u'手机'

    def get_name(self, obj):
        return obj.user.wanglibaouserprofile.name
    get_name.short_description = u'姓名'

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


class BankAdmin(admin.ModelAdmin):
    list_display = ('name', 'gate_id', 'code', "kuai_code")

    def has_delete_permission(self, request, obj=None):
        return False


class CardAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('get_phone', 'no', 'bank')
    search_fields = ['user__wanglibaouserprofile__phone', 'no']
    raw_id_fields = ('user', 'bank')

    def get_phone(self, obj):
        return obj.user.wanglibaouserprofile.phone

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    get_phone.short_description = u'手机'


class WithdrawCardAdmin(admin.ModelAdmin):
    list_display = ('bank', 'bank_name', 'card_name', 'card_no', 'amount', 'freeze', 'is_default')

    def get_readonly_fields(self, request, obj=None):
        return ('amount', 'freeze')

    def has_delete_permission(self, request, obj=None):
        return False


class WithdrawCardRecordAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'type', 'withdrawcard', 'amount', 'fee', 'management_fee', 'management_amount',
                    'user', 'create_time', 'status', 'message')
    raw_id_fields = ('user', 'payinfo', 'order')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


class WhiteListCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_no', 'message', 'create_time')
    raw_id_fields = ('user', )
    search_fields = ('=user__wanglibaouserprofile__phone', '=card_no')


class BlackListCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_no', 'message', 'ip', 'create_time')
    raw_id_fields = ('user', )
    search_fields = ('=user__wanglibaouserprofile__phone', '=card_no')


admin.site.register(Bank, BankAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(PayInfo, PayInfoAdmin)
admin.site.register(WithdrawCard, WithdrawCardAdmin)
admin.site.register(WithdrawCardRecord, WithdrawCardRecordAdmin)
admin.site.register(WhiteListCard, WhiteListCardAdmin)
admin.site.register(BlackListCard, BlackListCardAdmin)


admin.site.register_view('pay/withdraw/audit', view=WithdrawTransactions.as_view(), name=u'提现申请审核页面')
admin.site.register_view('pay/withdraw/rollback', view=WithdrawRollback.as_view(), name=u'提现申请失败回滚页面')

admin.site.register_view('pay/transaction', view=AdminTransaction.as_view(),name=u'交易记录详情')


