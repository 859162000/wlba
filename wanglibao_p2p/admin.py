# coding=utf-8
from concurrency.admin import ConcurrentModelAdmin
import datetime
from django.contrib import admin
from reversion.admin import VersionAdmin
from models import P2PProduct, Warrant, WarrantCompany, P2PRecord, P2PEquity, Attachment, ContractTemplate
from models import AmortizationRecord, ProductAmortization, EquityRecord, UserAmortization
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin


class UserEquityAdmin(ConcurrentModelAdmin, VersionAdmin):
    list_display = (
        'user', 'product', 'equity', 'confirm', 'ratio', 'paid_principal', 'paid_interest', 'penal_interest')
    list_filter = ('confirm',)


class AmortizationInline(admin.TabularInline):
    model = ProductAmortization
    extra = 0
    exclude = ('version',)
    can_delete = False
    readonly_fields = ('term', 'term_date', 'principal', 'interest', 'penal_interest', 'ready_for_settle', 'description')


class WarrantInline(admin.TabularInline):
    model = Warrant


class AttachementInline(admin.TabularInline):
    model = Attachment


class P2PEquityInline(admin.TabularInline):
    model = P2PEquity
    raw_id_fields = ('user',)
    readonly_fields = ('user', 'confirm', 'contract', 'equity', 'confirm_at')
    exclude = ('version',)
    extra = 0
    can_delete = False

    def get_queryset(self, request):
        return super(P2PEquityInline, self).get_queryset(request).select_related('user').select_related(
            'user__wanglibaouserprofile')


class P2PProductResource(resources.ModelResource):
    count = 4

    class Meta:
        model = P2PProduct
        fields = ('id', 'name', 'serial_number', 'contract_serial_number', 'borrower_bankcard_bank_name')

    def import_obj(self, instance, row, false):
        super(P2PProductResource, self).import_obj(instance, row, false)
        # todo update later

        now = datetime.datetime.now().date().strftime('%Y%m%d')
        self.count += 1
        type = row[u'产品名称']
        print row[u'出生日期']
        #birthday = datetime.date(row[u'出生日期'])
        #today = datetime.date.today()
        #age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
        instance.name = u"网利%s %s%s" % (row[u'产品名称'], now, str(self.count).zfill(3))
        instance.short_name = instance.name
        instance.serial_number = "E_ZDSD_%s" % (str(self.count).zfill(5))
        instance.contract_serial_number = row[u'合同编号']
        instance.priority = 0
        instance.period = row[u'申请还款期限（月）']
        instance.expected_earning_rate = 12
        instance.excess_earning_rate = 0
        instance.pay_method = "等额本息"

        instance.borrower_name = row[u'姓名']
        instance.borrower_phone = row[u'手机号码']
        instance.borrower_address = row[u'现住址']
        instance.borrower_id_number = row[u'身份证号码']
        instance.borrower_bankcard = row[u'提现帐号']
        instance.borrower_bankcard_bank_name = row[u'开户行']
        for bank in P2PProduct.BANK_METHOD_CHOICES:
            if bank[0] in instance.borrower_bankcard_bank_name:
                instance.borrower_bankcard_bank_code = bank

        instance.total_amount = row[u'申请贷款金额（元）']
        instance.end_time = datetime.datetime.now() + datetime.timedelta(days=2)
        instance.usage = row[u'贷款用途']
        instance.short_usage = row[u'贷款用途']

        if type == u"工薪贷":
            instance.extra_data = u'{"个人信息":{"用户ID":%s,"性别":%s,"出生日期":%s,"学历":%s,"是否结婚":%s,"子女状况":%s,"户籍城市":%s},' \
                                  u'"个人资产及征信信息":{"月收入水平":%s,"房产":%s,"车产":%s},' \
                                  u'"工作信息":{"工作城市":%s,"现公司工作时间":%s,"公司行业":%s,"公司性质":%s,"所在部门":%s}}' \
                                  % (row[u'姓名'], row[u'性别'], row[u'出生日期'], row[u'学历'], row[u'是否结婚'], row[u'子女状况'], row[u'户籍城市'],
                                     row[u'个人月收入（元）'], row[u'有无房产'], row[u'有无车产'],
                                     row[u'工作城市'], row[u'工作时间'], row[u'公司行业'], row[u'公司性质'], row[u'所在部门'])
        if type == u"企业贷":
            instance.extra_data = u'{"个人信息":{"用户ID":%s,"性别":%s,"出生日期":%s,"是否结婚":%s,"子女状况":%s,"户籍城市":%s},' \
                                  u'"企业经营信息":{"月销售收入（元）":%s,"房产":%s,"车产":%s},' \
                                  u'"企业信息":{"企业所在城市":%s,"企业规模":%s,"所属行业":%s,"企业类型":%s,"成立时间":%s,"企业地址":%s}}' \
                                  % (row[u'姓名'], row[u'性别'], row[u'出生日期'], row[u'是否结婚'], row[u'子女状况'], row[u'户籍城市'],
                                     row[u'月销售收入（元）'], row[u'有无房产'], row[u'有无车产'],
                                     row[u'企业所在城市'], row[u'企业规模'], row[u'所属行业'], row[u'企业类型'], row[u'成立时间'], row[u'企业地址'])

        instance.warrant_company = WarrantCompany.objects.get(name='证大速贷')
        instance.contract_template = ContractTemplate.objects.get(name='正大速贷')


class P2PProductAdmin(ImportExportModelAdmin, ConcurrentModelAdmin, VersionAdmin):
    inlines = [
        WarrantInline, AttachementInline, AmortizationInline, P2PEquityInline
    ]
    list_display = ('name', 'short_name', 'status', 'pay_method', 'end_time', 'audit_link', 'preview_link', 'priority')
    list_editable = ('status', 'priority')
    list_filter = ('status',)
    search_fields = ('name',)
    readonly_fields = ('amortization_count',)
    resource_class = P2PProductResource
    change_list_template = 'change_list.html'
    from_encoding = 'utf-8'


class UserAmortizationAdmin(ConcurrentModelAdmin, VersionAdmin):
    list_display = ('product_amortization', 'user', 'principal', 'interest', 'penal_interest')


class P2PRecordAdmin(admin.ModelAdmin):
    list_display = (
        'catalog', 'order_id', 'product', 'user', 'amount', 'product_balance_after', 'create_time', 'description')


class WarrantAdmin(admin.ModelAdmin):
    list_display = ('product', 'name')


class AmortizationRecordAdmin(admin.ModelAdmin):
    list_display = (
        'catalog', 'order_id', 'amortization', 'user', 'term', 'principal', 'interest', 'penal_interest', 'description')


class EquityRecordAdmin(admin.ModelAdmin):
    list_display = ('catalog', 'order_id', 'product', 'user', 'amount', 'create_time', 'description')


admin.site.register(P2PProduct, P2PProductAdmin)
admin.site.register(Warrant, WarrantAdmin)
admin.site.register(P2PEquity, UserEquityAdmin)
admin.site.register(WarrantCompany)
admin.site.register(UserAmortization, UserAmortizationAdmin)
admin.site.register(ContractTemplate)
admin.site.register(P2PRecord, P2PRecordAdmin)
admin.site.register(EquityRecord, EquityRecordAdmin)
admin.site.register(AmortizationRecord, AmortizationRecordAdmin)
