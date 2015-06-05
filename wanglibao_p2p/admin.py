# coding=utf-8
from collections import OrderedDict
from concurrency.admin import ConcurrentModelAdmin
import datetime
from django.contrib import admin, messages
from django import forms
from django.forms import formsets
from django.utils import timezone
from reversion.admin import VersionAdmin
from models import P2PProduct, Warrant, WarrantCompany, P2PRecord, P2PEquity, Attachment, ContractTemplate, Earning,\
    P2PProductContract, InterestPrecisionBalance, ProductInterestPrecision, InterestInAdvance, AutomaticPlan, AutomaticManager
from models import AmortizationRecord, ProductAmortization, EquityRecord, UserAmortization, P2PEquityJiuxian
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin, ExportMixin
from wanglibao_p2p.views import GenP2PUserProfileReport, AdminAmortization, AdminPrepayment, AdminP2PList
from wanglibao.admin import ReadPermissionModelAdmin
from wanglibao_p2p.forms import RequiredInlineFormSet
from wanglibao_account.models import UserAddress
from wanglibao_p2p.tasks import automatic_trade

formsets.DEFAULT_MAX_NUM = 2000


class UserEquityResource(resources.ModelResource):
    id = fields.Field(attribute="id", column_name=u"持仓ID")
    user = fields.Field(attribute="user__wanglibaouserprofile__phone", column_name=u"用户手机号")
    product = fields.Field(attribute="product__name", column_name=u"产品名称")
    equity = fields.Field(attribute="equity", column_name=u"用户所持份额")
    created_at = fields.Field(attribute="created_at", column_name=u"持仓时间")

    class Meta:
        model = P2PEquity
        fields = ('id', 'user', 'product', 'equity', 'created_at')
        export_order = ('id', 'user', 'product', 'equity', 'created_at')

    def dehydrate_created_at(self, obj):
        return timezone.localtime(obj.created_at).strftime("%Y-%m-%d %H:%M:%S")


class UserEquityAdmin(ExportMixin, admin.ModelAdmin):
    list_display = (
        'id', 'user', 'product', 'equity', 'confirm', 'confirm_at', 'ratio', 'paid_principal', 'paid_interest',
        'penal_interest')
    list_filter = ('confirm',)
    search_fields = ('product__name', 'user__wanglibaouserprofile__phone')
    raw_id_fields = ('user', 'product')
    resource_class = UserEquityResource

    def get_readonly_fields(self, request, obj=None):
        if not request.user.has_perm('wanglibao_p2p.view_p2pequity'):
            return [f.name for f in self.model._meta.fields]
        return ()

    def get_export_filename(self, file_format):
        date_str = timezone.now().strftime('%Y-%m-%d')
        filename = "%s-%s.%s" % (u"用户持仓".encode('utf-8'),
                                 date_str,
                                 file_format.get_extension())
        return filename


class AmortizationInline(admin.TabularInline):
    model = ProductAmortization
    extra = 0
    exclude = ('version',)
    can_delete = False
    # readonly_fields = (
    #     'term', 'principal', 'interest', 'penal_interest', 'description')

    def get_readonly_fields(self, request, obj=None):
        read_only = ['term', 'principal', 'interest', 'penal_interest', 'description']
        if obj and obj.status == u'已完成':
            read_only.append('ready_for_settle')
        return tuple(read_only)


class WarrantInline(admin.TabularInline):
    model = Warrant


class P2PProductContractInline(admin.StackedInline):
    model = P2PProductContract
    extra = 1
    max_num = 1
    formset = RequiredInlineFormSet


class AttachementInline(admin.TabularInline):
    model = Attachment


class P2PEquityInline(admin.TabularInline):
    model = P2PEquity
    raw_id_fields = ('user',)
    readonly_fields = ('user', 'confirm', 'contract', 'equity', 'confirm_at')
    exclude = ('version',)
    extra = 0
    can_delete = False
    list_max_show_all = 1

    def get_queryset(self, request):
        return super(P2PEquityInline, self).get_queryset(request).select_related('user').select_related(
            'user__wanglibaouserprofile')


class P2PProductResource(resources.ModelResource):
    count = 0

    class Meta:
        model = P2PProduct
        fields = ('id', 'name', 'serial_number', 'contract_serial_number', 'borrower_bankcard_bank_name')

    def import_obj(self, instance, row, false):
        super(P2PProductResource, self).import_obj(instance, row, false)

        now = datetime.datetime.now().date().strftime('%Y%m%d')
        self.count += 1
        type = row[u'产品名称']
        # birthday = datetime.date(row[u'出生日期'])
        # today = datetime.date.today()
        #age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
        instance.category = u"证大速贷"
        instance.serial_number = "E_ZDSD_%s%s" % (now, str(self.count).zfill(5))
        instance.contract_serial_number = row[u'合同编号']
        instance.priority = 0
        instance.period = row[u'申请还款期限（月）']
        instance.expected_earning_rate = 12.5
        instance.excess_earning_rate = 0
        if int(instance.period) <= 18:
            instance.excess_earning_rate = 0.5
            instance.excess_earning_description = u"网利宝活动补贴"
        instance.pay_method = u"等额本息"

        instance.borrower_name = row[u'姓名']
        instance.borrower_phone = row[u'手机号码']
        instance.borrower_address = row[u'现住址']
        instance.borrower_id_number = row[u'身份证号码']
        instance.borrower_bankcard = row[u'提现帐号']
        instance.borrower_bankcard_bank_name = row[u'开户行']

        for bank in P2PProduct.BANK_METHOD_CHOICES:
            if bank[0] in instance.borrower_bankcard_bank_name:
                instance.borrower_bankcard_bank_code = bank[0]

        instance.total_amount = row[u'申请贷款金额（元）']
        instance.end_time = datetime.datetime.now() + datetime.timedelta(days=2)
        #instance.usage = row[u'贷款用途']
        #instance.short_usage = row[u'贷款用途']
        month_income = int(row[u'个人月收入（元）'])
        month_income_str = ""
        if month_income <= 2000:
            month_income_str = u"0-2000元"
        if month_income > 2000 and month_income < 5000:
            month_income_str = u"2000元-5000元"
        if month_income >= 5000 and month_income < 8000:
            month_income_str = u"5000元-8000元"
        if month_income >= 8000 and month_income <= 12000:
            month_income_str = u"8000元-12000元"
        if month_income > 12000 and month_income <= 18000:
            month_income_str = u"12000元-18000元"
        if month_income > 18000:
            month_income_str = u"18000元以上"

        if type == u"工薪族":
            instance.name = u"%s%s%s" % (u"工薪日常消费", str(now)[2:], str(self.count).zfill(3))
            instance.extra_data = OrderedDict([
                (u'个人信息', OrderedDict([
                    (u'性别', row[u'性别']),
                    (u'出生日期', row[u'出生日期']),
                    (u'学历', row[u'学历']),
                    (u'是否已婚', row[u'是否结婚']),
                    (u'子女状况', row[u'子女状况']),
                    (u'户籍城市', row[u'户籍城市'])
                ])),
                (u'个人资产及征信信息', OrderedDict([
                    (u'月收入水平', month_income_str),
                    (u'房产', row[u'有无房产']),
                    (u'车产', row[u'有无车产'])
                ])),
                (u'工作信息', OrderedDict([
                    (u'工作城市', row[u'工作城市']),
                    (u'现公司工作时间', row[u'工作时间']),
                    (u'公司行业', row[u'公司行业']),
                    (u'公司性质', row[u'公司性质']),
                    (u'岗位', row[u'岗位（职务）'])
                ]))
            ])

        if type == u"企业主":
            instance.name = u"%s%s%s" % (u"企业扩大经营", str(now)[2:], str(self.count).zfill(3))
            instance.extra_data = OrderedDict([
                (u'个人信息', OrderedDict([
                    (u'性别', row[u'性别']),
                    (u'出生日期', row[u'出生日期']),
                    (u'学历', row[u'学历']),
                    (u'是否已婚', row[u'是否结婚']),
                    (u'子女状况', row[u'子女状况']),
                    (u'户籍城市', row[u'户籍城市']),
                    (u'月收入水平', month_income_str)
                ])),
                (u'企业经营信息', OrderedDict([
                    (u'月销售收入(元)', row[u'月销售收入（元）']),
                    (u'房产', row[u'有无房产']),
                    (u'车产', row[u'有无车产'])
                ])),
                (u'企业信息', OrderedDict([
                    (u'企业所在城市', row[u'企业所在城市']),
                    (u'企业规模', row[u'企业规模']),
                    (u'所属行业', row[u'所属行业']),
                    (u'企业类型', row[u'企业类型']),
                    (u'成立时间', row[u'成立时间']),
                    (u'企业地址', row[u'企业地址'])
                ]))
            ])
        instance.short_name = instance.name
        instance.warrant_company = WarrantCompany.objects.get(name='证大速贷')
        instance.contract_template = ContractTemplate.objects.get(name='证大速贷')


class P2PProductForm(forms.ModelForm):
    serial_number = forms.CharField(label=u'产品编号*', required=True, max_length=100, widget=forms.TextInput(attrs={'class': 'vTextField'}))
    
    class Meta:
        model = P2PProduct
    
    def clean_period(self):
        period = self.cleaned_data.get('period')
        if period == 0:
            raise forms.ValidationError(u'产品期限(月)必须大于零')
        return period    

    def clean_serial_number(self):
        serial_number = self.cleaned_data.get('serial_number')
        p2p_product = P2PProduct.objects.filter(pk=self.instance.pk)
        if p2p_product.exists(): # 校验已经存在的p2p产品, 先判断提交的表单数据中产品编号是否已修改
            if serial_number and serial_number != p2p_product[0].serial_number:
                if P2PProduct.objects.filter(serial_number=serial_number).exists():
                    raise forms.ValidationError(u'产品编号已存在，请重新填写')
        else: # 校验新添加的p2p产品
            if P2PProduct.objects.filter(serial_number=serial_number).exists():
                raise forms.ValidationError(u'产品编号已存在，请重新填写')
        return serial_number

    def clean(self):
        if self.cleaned_data.get('pay_method') == u'等额本息':
            if self.cleaned_data.get('expected_earning_rate') == float(0):
                raise forms.ValidationError(u'支付方式为等额本息时, 预期收益(%)必须大于零')

#        if self.cleaned_data['status'] == u'正在招标':
#
#            pa = ProductAmortization.objects.filter(product__version=self.cleaned_data['version'])
#
#            if not pa:
#                raise forms.ValidationError(u'产品状态必须先设置成[录标完成],之后才能改为[正在招标]')
#
#            product = P2PProduct.objects.filter(version=self.cleaned_data['version']).first()
#            if pa.count() != product.amortization_count:
#                raise forms.ValidationError(u'产品还款计划错误')
#
#            amort_principal = 0
#            for a in pa:
#                amort_principal += a.principal
#
#            if amort_principal != self.cleaned_data['total_amount']:
#                raise forms.ValidationError(u'还款计划本金之和与募集金额不相等，请检查')

        return self.cleaned_data


class P2PProductAdmin(ReadPermissionModelAdmin, ImportExportModelAdmin, ConcurrentModelAdmin, VersionAdmin):
    inlines = [
        P2PProductContractInline, WarrantInline, AttachementInline, AmortizationInline#, P2PEquityInline
    ]
    list_display = ('id', 'name', 'total_amount', 'brief', 'status', 'pay_method', 'end_time', 'warrant_company', 'audit_link', 'preview_link', 'preview_contract', 'copy_link', 'priority')
    list_editable = ('priority',)
    list_filter = ('status', )
    search_fields = ('name',)
    resource_class = P2PProductResource
    change_list_template = 'change_list.html'
    from_encoding = 'utf-8'


    form = P2PProductForm


    def get_readonly_fields(self, request, obj=None):
        if not request.user.has_perm('wanglibao_p2p.view_p2pproduct'):
            return [f.name for f in self.model._meta.fields]
        return ('amortization_count',)

    def save_model(self, request, obj, form, change):
        # if obj.status == u'正在招标':
        #     # todo remove the try except
        #     try:
        #         # 财经道购买回调
        #         params = CjdaoUtils.post_product(obj, CJDAOKEY)
        #         cjdao_callback.apply_async(kwargs={'url': POST_PRODUCT_URL, 'params': params})
        #     except:
        #         pass
        super(P2PProductAdmin, self).save_model(request, obj, form, change)

        """
        # 停止这个入口，从watch进入自动投标
        if obj and obj.status == u'正在招标':
            automatic_trade.apply_async(kwargs={
                "product_id": obj.id,
            })
        """


class UserAmortizationAdmin(ConcurrentModelAdmin, VersionAdmin):
    list_display = ('product_amortization', 'user', 'principal', 'interest', 'penal_interest')
    search_fields = ('user__wanglibaouserprofile__phone', 'product_amortization__product__name')
    raw_id_fields = ('product_amortization', 'user')


class P2PRecordResource(resources.ModelResource):
    user_name = fields.Field(attribute="user__wanglibaouserprofile__name", column_name=u'姓名')
    user_phone = fields.Field(attribute="user__wanglibaouserprofile__phone", column_name=u'手机号')
    product_name = fields.Field(attribute="product__name", column_name=u'产品名称')
    product_id = fields.Field(attribute="product__id", column_name=u'产品ID')

    class Meta:
        model = P2PRecord
        fields = ('user_name', 'user_phone', 'product_name', 'catalog', 'order_id', 'amount',
                  'product_balance_after', 'create_time', 'description')

    def dehydrate_create_time(self, obj):
        return timezone.localtime(obj.create_time).strftime("%Y-%m-%d %H:%M:%S")


class P2PRecordAdmin(ReadPermissionModelAdmin, ImportExportModelAdmin):
    list_display = (
        'catalog', 'order_id', 'product_id', 'product', 'user', 'amount', 'product_balance_after', 'create_time',
        'description', 'platform')
    resource_class = P2PRecordResource
    change_list_template = 'admin/import_export/change_list_export.html'
    search_fields = ('user__wanglibaouserprofile__phone','product__name')
    list_filter = ('catalog', )

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def product_id(self, obj):
        return "%s" % obj.product.id


class WarrantAdmin(admin.ModelAdmin):
    list_display = ('product', 'name')


class AmortizationRecordAdmin(admin.ModelAdmin):
    list_display = (
        'catalog', 'order_id', 'amortization', 'user', 'term', 'principal', 'interest', 'penal_interest', 'description')
    search_fields = ('user__wanglibaouserprofile__phone',)
    raw_id_fields = ('amortization', 'user')


class EquityResource(resources.ModelResource):
    order_id = fields.Field(attribute="order_id", column_name=u"流水号")
    user = fields.Field(attribute="user__wanglibaouserprofile__phone", column_name=u"用户手机号")
    product = fields.Field(attribute="product__name", column_name=u"产品名称")
    amount = fields.Field(attribute="amount", column_name=u"所持份额")
    create_time = fields.Field(attribute="create_time", column_name=u"流水时间")
    description = fields.Field(attribute="description", column_name=u"摘要信息")

    class Meta:
        model = EquityRecord
        fields = ('order_id', 'user', 'product', 'amount', 'create_time', 'description')
        export_order = ('order_id', 'user', 'product', 'amount', 'create_time', 'description')

    def dehydrate_create_time(self, obj):
        return timezone.localtime(obj.create_time).strftime("%Y-%m-%d %H:%M:%S")


class EquityRecordAdmin(ExportMixin, ReadPermissionModelAdmin):
    list_display = ('catalog', 'order_id', 'product', 'user', 'amount', 'create_time', 'description')
    search_fields = ('user__wanglibaouserprofile__phone', 'product__name')
    resource_class = EquityResource

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def get_export_filename(self, file_format):
        date_str = timezone.now().strftime('%Y-%m-%d')
        filename = "%s-%s.%s" % (u"持仓流水".encode('utf-8'),
                                 date_str,
                                 file_format.get_extension())
        return filename


class ProductAmortizationAdmin(ReadPermissionModelAdmin):
    list_display = ('id', 'product', 'term', 'term_date', 'principal', 'interest', 'penal_interest', 'settled',
                    'settlement_time', 'created_time', 'status', 'description', )

    search_fields = ('product__name', 'product__serial_number')

    def status(self, obj):
        if obj.product:
            status = obj.product.status
        else:
            status = ''

        return status


class EarningAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'amount', )
    raw_id_fields = ('order', 'margin_record', 'user', 'product',)
    search_fields = ('user__wanglibaouserprofile__phone',)



    def get_readonly_fields(self, request, obj=None):
        if not request.user.has_perm('wanglibao_p2p.view_productamortization'):
            return [f.name for f in self.model._meta.fields]
        return ()


class P2PProductContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'signing_date', 'party_b', 'party_b_name', 'party_c', 'party_c_name',
                    'party_c_id_number', 'party_c_address', 'bill_drawer_bank', 'bill_accepting_bank',
                    'bill_number', 'bill_amount', 'bill_due_date')



class InterestPrecisionAdmin(admin.ModelAdmin):
    list_display = ('id', 'equity_product', 'equity_phone', 'equity_name', 'equity_number',
                    'principal', 'interest_receivable', 'interest_actual', 'balance',)
    raw_id_fields = ('equity',)
    search_fields = ('equity__product__id', 'equity__product__name', 'equity__user__wanglibaouserprofile__phone',)

    def equity_phone(self, instance):
        return instance.equity.user.wanglibaouserprofile.phone

    def equity_product(self, instance):
        return instance.equity.product.name

    def equity_name(self, instance):
        return instance.equity.user.wanglibaouserprofile.name

    def equity_number(self, instance):
        return instance.equity.user.wanglibaouserprofile.id_number

    def balance(self, instance):
        from decimal import Decimal
        if instance.interest_precision_balance == Decimal('0'):
            return Decimal(0)
        return instance.interest_precision_balance


class InterestInAdvanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'interest')


class ProductInterestPrecisionAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_name', 'principal', 'interest_receivable',
                    'interest_actual', 'balance',)
    search_fields = ('product__id', 'product__name')


    def product_name(self, instance):
        return instance.product.name

    def balance(self, instance):
        from decimal import Decimal
        if instance.interest_precision_balance == Decimal('0'):
            return Decimal(0)
        return instance.interest_precision_balance


class EquityJiuxianResource(resources.ModelResource):
    user = fields.Field(attribute="user__wanglibaouserprofile__phone", column_name=u"用户手机号")
    product = fields.Field(attribute="product__name", column_name=u"产品名称")
    equity_amount = fields.Field(attribute="equity_amount", column_name=u"所持份额")
    selected_type = fields.Field(attribute="selected_type", column_name=u"选择收益类型")
    address = fields.Field(attribute="address", column_name=u"地址信息")

    class Meta:
        model = P2PEquityJiuxian
        fields = ('user', 'product', 'equity_amount', 'selected_type', 'address')
        export_order = ('user', 'product', 'equity_amount', 'selected_type', 'address')

    def dehydrate_selected_type(self, obj):
        if obj.selected_type == 'wine':
            return u'酒 + 收益'
        else:
            return u'本金 + 收益'

    def dehydrate_address(self, obj):
        address = ''
        addr_infos = UserAddress.objects.filter(user=obj.user, is_default=True).first()
        if addr_infos:
            address = '//'.join([addr_infos.name, addr_infos.phone_number, addr_infos.address, addr_infos.postcode])
        else:
            addr_infos = UserAddress.objects.filter(user=obj.user).order_by('-id').first()
            if addr_infos:
                address = '//'.join([addr_infos.name, addr_infos.phone_number, addr_infos.address, addr_infos.postcode])

        return address


class P2PEquityJiuxianAdmin(ExportMixin, admin.ModelAdmin):
    actions = None
    list_display = ('id', 'user', 'product', 'equity_amount', 'selected_type',
                    'selected_at')
    resource_class = EquityJiuxianResource

    def get_export_filename(self, file_format):
        date_str = timezone.now().strftime('%Y-%m-%d')
        filename = "%s-%s.%s" % (u"酒仙众筹标用户投资记录".encode('utf-8'),
                                 date_str,
                                 file_format.get_extension())
        return filename

    def __init__(self, *args, **kwargs):
        super(P2PEquityJiuxianAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

    # def has_add_permission(self, request):
    #     return False
    #
    def has_delete_permission(self, request, obj=None):
        return False


class AutomaticPlanAdmin(admin.ModelAdmin):
    display = ('id', 'user', 'amounts_auto', 'amounts_left', 'period_min', 'period_max', 'rate_min', 'rate_max', 'last_updated', 'is_used')
    list_display = display
    readonly_fields = display
    raw_id_fields = ('user',)
    search_fields = ('user__wanglibaouserprofile__phone',)
    ordering = ('id', '-last_updated')


class AutomaticManagerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'stop_plan', 'start_at', 'end_at', 'last_updated', 'is_used', 'message')
    ordering = ('id', '-last_updated')


admin.site.register(P2PProduct, P2PProductAdmin)
admin.site.register(Warrant, WarrantAdmin)
admin.site.register(P2PEquity, UserEquityAdmin)
admin.site.register(WarrantCompany)
admin.site.register(UserAmortization, UserAmortizationAdmin)
admin.site.register(ContractTemplate)
admin.site.register(P2PRecord, P2PRecordAdmin)
admin.site.register(EquityRecord, EquityRecordAdmin)
admin.site.register(AmortizationRecord, AmortizationRecordAdmin)
admin.site.register(ProductAmortization, ProductAmortizationAdmin)
admin.site.register(Earning, EarningAdmin)
admin.site.register(P2PProductContract, P2PProductContractAdmin)
admin.site.register(InterestPrecisionBalance, InterestPrecisionAdmin)
admin.site.register(InterestInAdvance, InterestInAdvanceAdmin)
admin.site.register(ProductInterestPrecision, ProductInterestPrecisionAdmin)
admin.site.register(P2PEquityJiuxian, P2PEquityJiuxianAdmin)
admin.site.register(AutomaticPlan, AutomaticPlanAdmin)
admin.site.register(AutomaticManager, AutomaticManagerAdmin)

admin.site.register_view('p2p/userreport', view=GenP2PUserProfileReport.as_view(), name=u'生成p2p用户表')
admin.site.register_view('p2p/amortization', view=AdminAmortization.as_view(), name=u'还款计算器')
admin.site.register_view('p2p/prepayment/(?P<id>\w+)', view=AdminPrepayment.as_view(), name=u'待优化')
admin.site.register_view('p2p/p2plist', view=AdminP2PList.as_view(), name=u'还款中标的')
